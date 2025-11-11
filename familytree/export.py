import json
from typing import List
from .models import Person


def save_tree_to_json(people: List[Person], filename: str = "family_tree.json"):
    """
    Save the generated family tree to a JSON file.
    """
    data = [p.to_dict() for p in people]

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Family tree saved to {filename}")
