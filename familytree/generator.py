from collections import deque
import bisect
import random
from typing import List, Tuple
from .models import Person
import time
import json


def pair_people(people: List[Person]) -> List[Tuple[Person, Person]]:
    """
    Extremely fast pairing for same-generation populations:
    - Pairs men and women randomly (no need to compare ages).
    - Avoids pairing siblings (shared parents).
    - Runs in O(n) average time.
    """
    males = [p for p in people if p.gender == "M"]
    females = [p for p in people if p.gender == "F"]
    couples = []

    # Convert to dictionaries for constant-time parent lookup
    female_parents = [set(f.parents) for f in females]

    i = 0
    while i < len(males) and females:
        man = males[i]
        m_parents = set(man.parents)

        # Buscar la primera mujer que no comparta padres
        found = False
        for k in range(len(females)):
            f_parents = female_parents[k]
            if not m_parents or not f_parents or m_parents != f_parents:
                woman = females.pop(k)
                couples.append((man, woman))

                # Eliminar a la mujer usada moviéndola al final y cortando el array
                female_parents.pop(k)
                found = True
                break

        i += 1
        if not found:
            # Si no hay ninguna mujer elegible, pasa a la siguiente
            continue

    return couples

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
    Generate a family tree generation by generation and write incrementally to JSON.
    This reduces memory usage by freeing previous generations.
    """
    population = initial_people
    current_year = min(p.birth_year for p in population)
    first_gen = True

    # Abrir el archivo y escribir el '[' inicial
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("[\n")

    for gen_num in range(generations):

        print(f"\n --- Generation {gen_num + 1} --- ")
        start_gen_time = time.time()

        # Emparejar personas
        start_pair_time = time.time()
        couples = pair_people(population)
        pair_time = time.time() - start_pair_time
        print(f"Paired {len(couples)} couples in {pair_time:.2f} seconds.")

        # Crear hijos
        start_children_time = time.time()
        new_generation = []

        for couple in couples:
            children = create_children(couple, name_pool, current_year + 25)
            new_generation.extend(children)
        children_time = time.time() - start_children_time
        print(f"Created {len(new_generation)} children in {children_time:.2f} seconds.")

        # Escribir la generación al JSON
        start_write_time = time.time()
        with open(output_file, "a", encoding="utf-8") as f:
            for i, person in enumerate(new_generation):
                json.dump(person.to_dict(), f, ensure_ascii=False, indent=2)
                if gen_num != generations - 1 or i != len(new_generation) - 1:
                    f.write(",\n")  # coma entre objetos, excepto al final
        write_time = time.time() - start_write_time
        print(f"Wrote generation to JSON in {write_time:.2f} seconds.")

        # Tiempo total de la generación
        gen_time = time.time() - start_gen_time
        print(f"Generation {gen_num + 1} completed in {gen_time:.2f} seconds with {len(new_generation)} individuals.")

        # Liberar memoria de la generación anterior
        del population
        population = new_generation
        current_year += 25

    # Cerrar el JSON correctamente
    with open(output_file, "a", encoding="utf-8") as f:
        f.write("\n]\n")
