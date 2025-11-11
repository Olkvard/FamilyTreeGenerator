# FamilyTreeGenerator

**FamilyTreeGenerator** is a simple procedural generator that creates fictional family trees automatically.  
It pairs people, generates children based on rules, and saves the full genealogy as a JSON file.

---

## Features
- Automatic pairing of males and females by birth year similarity.
- Randomized name and gender generation for children.
- Iterative creation of multiple generations.
- Export of full genealogy data to JSON format.
- Easily extendable for visualization (e.g., Graphviz, NetworkX, D3.js).

---

## Project Structure
```bash
familytree/
├── models.py # Person class definition
├── generator.py # Core generation logic
└── export.py # Export utilities (JSON, etc.)
data/
scripts/
tests/
```

---


## Installation
```bash
git clone https://github.com/<your-username>/FamilyTreeGenerator.git
cd FamilyTreeGenerator
pip install -r requirements.txt
```
---
## Example Usage
You can run the script "scripts/run_example.py":

---
## Output
Running the above example will create a file called family_tree.json similar to:
```bash
[
  {
    "id": "e3d4...",
    "name": "Adam",
    "gender": "M",
    "birth_year": 0,
    "generation": 0,
    "parents": [],
    "children": ["a1b2...", "b2c3..."]
  },
  ...
]
```

---

## License
This project is licensed under the MIT License -- feel free to use, modify, and share it for any purpose.