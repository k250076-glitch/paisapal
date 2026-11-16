# PaisaPal design document

This document grows with the project. Each part adds the section for the
code it builds, so it always matches what is in the repository.

Status: up to date with Part 1 (project setup and agreed interfaces).

## 1. What the program does

PaisaPal is a menu-driven Python console app. The user types an expense in
plain words, such as "Rs 850 foodpanda biryani" or "uber to uni". The program
cleans the text, predicts the category, saves the expense, checks it against
the monthly budget, can convert foreign currency to PKR, and draws charts.

## 2. How the program runs, start to finish

1. `main.py` starts and loads the saved ledger and budgets (Parts 4 and 5).
2. It trains the classifier on `data/raw/expenses_labelled.csv`, or the user
   trains it from the menu (Parts 6 and 8).
3. The menu loop shows the options, reads a choice and calls one function for
   that choice (Part 13).
4. Adding an expense: the note is cleaned (Part 3), the classifier predicts a
   category (Part 8), the user accepts or corrects it, an `ExpenseTransaction`
   is created (Part 2) and added to the `Ledger` (Part 5).
5. Summaries use the NumPy matrix and Pandas (Parts 7 and 9). Charts are saved
   to `outputs/figures` (Parts 11 and 12).
6. On exit, the ledger and budgets are saved to `data/processed` (Part 4).

## 3. Project layout and who owns what

| File | Owner | Main data structure or algorithm |
|---|---|---|
| `src/models.py` | Polani | Abstract base class and inheritance, list (Ledger), dict (Budget) |
| `src/main.py` | Polani | Menu loop |
| `src/text_utils.py` | Zain | Set (stop-words), dict (normalisation map) |
| `src/classifier.py` | Zain | TF-IDF, Naive Bayes, Logistic Regression |
| `src/data_io.py` | Nehal | Tuple records, CSV and JSON files, custom exception |
| `src/api_client.py` | Nehal | Dict cache of exchange rates |
| `src/analysis.py` | Nehal | 2-D NumPy array, Pandas DataFrame |
| `src/plots.py` | Nehal, Zain | Matplotlib and Seaborn charts |

## 4. Data

- `data/raw/expenses_labelled.csv`: 1,640 short expense notes in English and
  Roman Urdu, each labelled with one of 8 categories. Used to train and test
  the classifier. It is a starter dataset made from templates of real-style
  notes (vendor names, items, Roman Urdu phrases, typos, amounts and payment
  apps mixed in). It contains no personal data.
- `data/raw/ledger_sample.csv`: about 270 dated transactions from June to
  November 2026, used for the NumPy, Pandas and chart work. Four rows are
  broken on purpose (missing amount, missing category, "abc" as amount, missing
  date) so the cleaning code has something to clean.

A record is passed around as a tuple:
`(date, description, amount, currency, category, kind)`.

## 5. Why we agreed the interfaces first

Part 1 created every module with the function names, inputs, outputs and time
complexity written in the docstrings, but without the code. That way each
member can build their part knowing exactly what the others' functions take
and return, and the parts fit together in Part 13.

## 6. Data structures and algorithms

Sections are added as each part is built.

## 7. Time and space complexity of the main operations

Filled in as each part is built.

| Operation | Time | Space |
|---|---|---|
