import json
from collections import Counter, defaultdict
from typing import Dict, List


def load_tree(filename: str = "family_tree.json") -> Dict[str, dict]:
    """
    Load the family tree JSON and return a dict of people keyed by ID.
    """
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {p["id"]: p for p in data}


def summarize_generations(people: Dict[str, dict]):
    """
    Print the number of people per generation.
    """
    gen_counter = Counter(p["generation"] for p in people.values())
    print("📊 People per generation:")
    for gen in sorted(gen_counter.keys()):
        print(f"  Generation {gen}: {gen_counter[gen]} people")
    print()


def gender_statistics(people: Dict[str, dict]):
    """
    Print the number of males and females.
    """
    gender_counter = Counter(p["gender"] for p in people.values())
    print("📊 Gender statistics:")
    print(f"  Males: {gender_counter.get('M', 0)}")
    print(f"  Females: {gender_counter.get('F', 0)}")
    print()


def latest_birth_year(people: Dict[str, dict]):
    """
    Print the most recent birth year (highest birth_year) among all people.
    """
    years = [p.get("birth_year") for p in people.values() if isinstance(p.get("birth_year"), int)]
    if not years:
        print("📅 Most recent birth year: no birth_year data available\n")
        return
    max_year = max(years)
    print("📅 Most recent birth year:")
    print(f"  Year: {max_year}")
    print()

def marriage_statistics(people: Dict[str, dict]):
    """
    Estimate number of marriages and average children per marriage.
    Marriage is counted as unique pairs of parents from the children.
    """
    marriages = defaultdict(list)  # key = tuple(parent IDs), value = list of children
    for p in people.values():
        if len(p["parents"]) == 2:
            key = tuple(sorted(p["parents"]))
            marriages[key].append(p["id"])

    print("📊 Marriage statistics:")
    print(f"  Number of marriages: {len(marriages)}")
    if marriages:
        avg_children = sum(len(c) for c in marriages.values()) / len(marriages)
        print(f"  Average children per marriage: {avg_children:.2f}")
    print()


def summarize_tree(filename: str = "family_tree.json"):
    """
    Load the tree and print a full summary.
    """
    people = load_tree(filename)
    total_people = len(people)
    print(f"🌳 Family Tree Summary ({filename})")
    print(f"Total people: {total_people}\n")

    summarize_generations(people)
    gender_statistics(people)
    marriage_statistics(people)
    latest_birth_year(people)



if __name__ == "__main__":
    summarize_tree()
