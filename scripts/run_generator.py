import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from familytree.models import Person
from familytree.generator import generate_family_tree_stream
from utils.analyze_tree import summarize_tree

DATA_DIR = "data"

def load_names():
    """Load male and female names from files."""
    with open(f"{DATA_DIR}/male_names.txt", "r", encoding="utf-8") as f:
        male_names = [line.strip() for line in f if line.strip()]

    with open(f"{DATA_DIR}/female_names.txt", "r", encoding="utf-8") as f:
        female_names = [line.strip() for line in f if line.strip()]

    return male_names, female_names

def main():
    # --- Configuración inicial ---
    generations = 20
    output_file = "family_tree.json"

    # --- Cargar nombres ---
    male_names, female_names = load_names()
    all_names = male_names + female_names  # pool para generación de hijos

    initial_people = [
        Person("Aerythiel", "F", 0),
        Person("Bryndalor", "M", 0),
        Person("Thalyssar", "M", 0),
    #    Person("Thalren", "M", 1),
        Person("Almyr", "F", 1),
    #    Person("Kaelyn", "F", 2),
    #    Person("Jothan", "M", 3),
    #    Person("Lytheris", "F", 4),
    #    Person("Vynathir", "M", 4),
    #    Person("Drayneth", "F", 5),
    #    Person("Zynariel", "F", 5),
    #    Person("Erythar", "M", 5)
    ]

    # --- Generar árbol ---
    generate_family_tree_stream(initial_people, all_names, generations=generations)

    # --- Mostrar resumen ---
    summarize_tree(output_file)


if __name__ == "__main__":
    main()
