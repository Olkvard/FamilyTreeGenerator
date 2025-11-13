import random
from typing import List, Tuple, Set
from .models import Person
import time
import json
import numpy as np


def pair_people(people: List[Person]) -> List[Tuple[Person, Person]]:
    """
    Vectorized pairing using precomputed parent_hash:
    - Pairs men and women randomly.
    - Avoids pairing siblings (same parent_hash) unless parent_hash == -1.
    - Works efficiently for large generations.
    """
    males = [p for p in people if p.gender == "M"]
    females = [p for p in people if p.gender == "F"]

    if not males or not females:
        return []

    n_m, n_f = len(males), len(females)
    n_pairs = min(n_m, n_f)

    # Convert parent_hashes to numpy arrays
    male_hashes = np.array([m.parent_hash for m in males], dtype=np.int64)
    female_hashes = np.array([f.parent_hash for f in females], dtype=np.int64)

    couples = []
    used_females = np.zeros(n_f, dtype=bool)

    # Shuffle males to randomize pairing
    male_indices = np.arange(n_m)
    np.random.shuffle(male_indices)

    for i in male_indices:
        m = males[i]
        mh = male_hashes[i]

        # Eligible females: different parent_hash or parent_hash == -1
        eligible_mask = (female_hashes != mh) | (female_hashes == -1) | (mh == -1)
        eligible_mask &= ~used_females

        eligible_idx = np.flatnonzero(eligible_mask)
        if eligible_idx.size == 0:
            continue

        # Pick a random eligible female
        j = np.random.choice(eligible_idx)
        used_females[j] = True
        couples.append((m, females[j]))

        if len(couples) >= n_pairs:
            break

    return couples


def pair_people_no_incest(people: List[Person]) -> List[Tuple[Person, Person]]:
    """
    Pair people while avoiding siblings and first cousins.
    Works even if not super efficient.
    """
    males = [p for p in people if p.gender == "M"]
    females = [p for p in people if p.gender == "F"]
    couples = []

    if not males or not females:
        return couples

    for man in males:
        eligible = []

        # Precompute man’s grandparents
        man_grandparents: Set[str] = set()
        for parent in man.parents:
            man_grandparents.update(p.id for p in parent.parents)

        for woman in females:
            # 1. No siblings
            siblings = man.parent_hash != -1 and man.parent_hash == woman.parent_hash

            # 2. No first cousins: si comparten algún abuelo
            woman_grandparents: Set[str] = set()
            for p in woman.parents:
                woman_grandparents.update(pp.id for pp in p.parents)

            cousins = bool(man_grandparents & woman_grandparents)

            if not siblings and not cousins:
                eligible.append(woman)

        if eligible:
            chosen = random.choice(eligible)
            couples.append((man, chosen))
            females.remove(chosen)  # remove to avoid reusing
        # else: no eligible partner, skip

    return couples


def pair_people_polygamy(people: List[Person]) -> List[Tuple[Person, Person]]:
    """
    Pair every man with all women possible, avoiding siblings and cousins.
    Each man can have children with all eligible women.
    """
    males = [p for p in people if p.gender == "M"]
    females = [p for p in people if p.gender == "F"]
    couples = []

    for man in males:
        man_grandparents = {pp.id for p in man.parents for pp in p.parents} if man.parents else set()
        for woman in females:
            # Evitar hermanos
            siblings = man.parents and woman.parents and any(p.id in [q.id for q in woman.parents] for p in man.parents)
            # Evitar primos
            woman_grandparents = {pp.id for p in woman.parents for pp in p.parents} if woman.parents else set()
            cousins = bool(man_grandparents & woman_grandparents)

            if not siblings and not cousins:
                couples.append((man, woman))  # se permiten múltiples parejas por mujer
    return couples



def create_children_polygamy(father, mother, name_pool, year):
    """
    Creates 1–6 children for a given couple.
    Each couple has its own parent_hash.
    """
    children = []
    # Probabilidad sesgada a tener más hijos
    weights = [1, 2, 4, 8, 16, 32, 64]
    num_children = random.choices(range(0, 7), weights=weights, k=1)[0]

    # Generar un hash único para esta pareja
    parent_hash = hash(f"{father.id}_{mother.id}")

    for _ in range(num_children):
        name = random.choice(name_pool)
        gender = random.choice(["M", "F"])
        birth_year = year + random.randint(0, 5)
        child = Person(name, gender, birth_year, parents=[father, mother])
        father.add_child(child)
        mother.add_child(child)
        children.append(child)

    return children

def create_children(parents, name_pool, year):
    """
    Creates 1–6 children for a given couple.
    """
    father, mother = parents
    children = []
    # Dar mayor probabilidad a números altos (0..6) usando pesos crecientes
    weights = [1, 2, 4, 8, 16, 32, 64]
    num_children = random.choices(range(0, 7), weights=weights, k=1)[0]

    for _ in range(num_children):
        name = random.choice(name_pool)
        gender = random.choice(["M", "F"])
        birth_year = year + random.randint(0, 5)
        child = Person(name, gender, birth_year, parents=[father, mother])
        father.add_child(child)
        mother.add_child(child)
        children.append(child)

    return children


def generate_family_tree_stream(initial_people: List[Person], name_pool: List[str],
                                generations: int, output_file: str = "family_tree.json"):
    """
    Generate a family tree generation by generation with polygamy support,
    writing incrementally to JSON to reduce memory usage.
    """
    population = initial_people
    current_year = min(p.birth_year for p in population)

    # Abrir el archivo y escribir '[' inicial
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("[\n")
        # Escribir la primera generación
        for i, person in enumerate(population):
            json.dump(person.to_dict(), f, ensure_ascii=False, indent=2)
            f.write(",\n")

    for gen_num in range(generations):
        print(f"\n --- Generation {gen_num + 1} --- ")
        start_gen_time = time.time()

        # Emparejar personas con poligamia
        start_pair_time = time.time()
        couples = pair_people(population)
        pair_time = time.time() - start_pair_time
        print(f"Paired {len(couples)} couples in {pair_time:.2f} seconds.")

        # Crear hijos
        start_children_time = time.time()
        new_generation = []
        for couples in couples:
            children = create_children(couples, name_pool, current_year + 25)
            new_generation.extend(children)
        # Alternativamente, usar poligamia:
        #for father, mother in couples:
        #    children = create_children_polygamy(father, mother, name_pool, current_year + 25)
        #    new_generation.extend(children)
        children_time = time.time() - start_children_time
        print(f"Created {len(new_generation)} children in {children_time:.2f} seconds.")

        # Escribir la generación al JSON
        start_write_time = time.time()
        with open(output_file, "a", encoding="utf-8") as f:
            for i, person in enumerate(new_generation):
                json.dump(person.to_dict(), f, ensure_ascii=False, indent=2)
                f.write(",\n")
        write_time = time.time() - start_write_time
        print(f"Wrote generation to JSON in {write_time:.2f} seconds.")

        # Tiempo total de la generación
        gen_time = time.time() - start_gen_time
        print(f"Generation {gen_num + 1} completed in {gen_time:.2f} seconds with {len(new_generation)} individuals.")

        # Liberar memoria de la generación anterior
        del population
        population = new_generation
        current_year += 25

    # Cerrar el JSON correctamente eliminando la última coma
    with open(output_file, "rb+") as f:
        f.seek(-2, 2)  # ir 2 bytes antes del final
        f.truncate()   # eliminar última coma
    with open(output_file, "a", encoding="utf-8") as f:
        f.write("\n]\n")
