import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from familytree.models import Person
from familytree.generator import generate_family_tree
from familytree.export import save_tree_to_json

# Initial population
initial_people = [
    Person("Adam", "M", 0),
    Person("Eve", "F", 0),
    Person("John", "M", 2),
    Person("Mary", "F", 3)
]

# Name pool for next generations
names = ["Alex", "Sophia", "Liam", "Emma", "Noah", "Olivia", "Lucas", "Mia"]

# Generate tree (3 generations)
tree = generate_family_tree(initial_people, names, generations=3)

# Save to file
save_tree_to_json(tree)