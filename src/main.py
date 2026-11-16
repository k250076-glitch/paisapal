"""
main.py - the console menu of PaisaPal (owner: Polani)

Run it from the project folder with:
    python src/main.py

The full menu is built in Part 13. For now it only checks that the project
is set up and that the sample data is in place.
"""

import os

# Folder of this file (src) and the project folder above it.
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SRC_DIR)

DATASET_PATH = os.path.join(PROJECT_DIR, "data", "raw", "expenses_labelled.csv")
LEDGER_PATH = os.path.join(PROJECT_DIR, "data", "raw", "ledger_sample.csv")


def main():
    """Print a welcome message and check that the sample data files exist."""
    print("PaisaPal - Smart Expense Categorizer and Budget Planner")
    for path in (DATASET_PATH, LEDGER_PATH):
        if os.path.exists(path):
            print("Found", os.path.relpath(path, PROJECT_DIR))
        else:
            print("Missing", os.path.relpath(path, PROJECT_DIR))
    print("Setup is complete. The menu is added in Part 13.")


if __name__ == "__main__":
    main()
