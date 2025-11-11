import random
from typing import List, Tuple
from .models import Person
import bisect


def pair_people(people: List[Person]) -> List[Tuple[Person, Person]]:
    """
    Optimized pairing:
    - Pairs men and women by closest birth year.
    - Avoids pairing siblings.
    - Efficient even with thousands of people.
    Returns a list of (man, woman) tuples.
    """
    # Separate and sort by birth_year
    males = sorted([p for p in people if p.gender == "M"], key=lambda p: p.birth_year)
    females = sorted([p for p in people if p.gender == "F"], key=lambda p: p.birth_year)

    couples = []

    # Convert females list to tuples (birth_year, person) for bisect
    female_years = [f.birth_year for f in females]

    while males and females:
        man = males.pop(0)
        
        # Find index of closest female by birth_year using bisect
        idx = bisect.bisect_left(female_years, man.birth_year)
        
        # Candidates: idx and idx-1
        candidates = []
        if idx < len(females):
            candidates.append(females[idx])
        if idx > 0:
            candidates.append(females[idx-1])

        # Filter out sisters (shared parents)
        eligible = [w for w in candidates if set(w.parents) != set(man.parents)]
        if not eligible:
            # If no eligible woman, consider all females
            eligible = females

        # Select the female closest in birth_year
        woman = min(eligible, key=lambda w: abs(w.birth_year - man.birth_year))

        # Remove selected woman from list efficiently
        remove_idx = females.index(woman)
        females.pop(remove_idx)
        female_years.pop(remove_idx)

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
