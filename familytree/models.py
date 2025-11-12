import uuid
from typing import List, Optional


class Person:
    """
    Represents a single person in the family tree.
    Stores a precomputed parent_hash for fast sibling checks.
    """

    def __init__(
        self,
        name: str,
        gender: str,
        birth_year: int,
        parents: Optional[List["Person"]] = None,
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.gender = gender  # 'M' or 'F'
        self.birth_year = birth_year
        self.parents = parents or []
        self.children: List["Person"] = []
        self.generation = (
            max((p.generation for p in self.parents), default=-1) + 1
        )

        # Compute parent hash: -1 if no parents
        if self.parents:
            self.parent_hash = hash(tuple(sorted(p.id for p in self.parents))) & 0xFFFFFFFF
        else:
            self.parent_hash = -1

    def add_child(self, child: "Person"):
        self.children.append(child)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "birth_year": self.birth_year,
            "generation": self.generation,
            "parents": [p.id for p in self.parents],
            "children": [c.id for c in self.children],
            "parent_hash": self.parent_hash,
        }

    def __repr__(self):
        return f"<Person {self.name} ({self.gender}) - Gen {self.generation}>"
