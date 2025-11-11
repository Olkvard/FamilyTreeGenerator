import random
from typing import List, Tuple
from .models import Person


def pair_people(people: List[Person]) -> List[Tuple[Person, Person]]:
    """
    Pair men and women by closest birth year, avoiding pairing siblings.
    Returns a list of (man, woman) tuples.
    """
    males = [p for p in people if p.gender == "M"]
    females = [p for p in people if p.gender == "F"]
    couples = []

    random.shuffle(males)
    random.shuffle(females)

    while males and females:
        man = males.pop(0)

        # Filtrar mujeres que no compartan padres con el hombre
        eligible_women = [
            w for w in females
            if set(w.parents) != set(man.parents)
        ]

        # Si no hay mujeres elegibles, permitir cualquier mujer (para no bloquear)
        if not eligible_women:
            eligible_women = females

        # Elegir la mujer con nacimiento más cercano
        woman = min(eligible_women, key=lambda w: abs(w.birth_year - man.birth_year))
        females.remove(woman)
        couples.append((man, woman))

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


def generate_family_tree(initial_people: List[Person], name_pool: List[str], generations: int):
    """
    Generate multiple generations of people based on initial individuals.
    """
    population = initial_people
    all_people = initial_people.copy()
    current_year = min(p.birth_year for p in population)

    for _ in range(generations):
        couples = pair_people(population)
        new_generation = []

        for couple in couples:
            children = create_children(couple, name_pool, current_year + 25)
            new_generation.extend(children)

        all_people.extend(new_generation)
        population = new_generation
        current_year += 25

    return all_people
