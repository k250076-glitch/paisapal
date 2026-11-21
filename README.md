# PaisaPal: Smart Expense Categorizer and Budget Planner

AL-2001 Programming for Artificial Intelligence (Lab), Fall 2026, FAST NUCES Karachi, BAI-3A.

PaisaPal is a menu-driven Python console app. You type an expense in plain words,
in English or Roman Urdu (for example "foodpanda biryani" or "careem to uni"). It
cleans the text, predicts the category with a trained classifier, lets you correct
it, tracks your monthly budgets, converts foreign currency to PKR and draws charts.

## Group

| Member | Roll no. | Module |
|---|---|---|
| Mustafa Muhammad Polani | 25K-0076 | Core classes, ledger, budget, menu |
| Zain Noman Dar | 25K-0146 | Text cleaning, TF-IDF, classifiers |
| Nehal Ali Khan | 25K-0133 | File I/O, currency API, NumPy/Pandas analysis, charts |

## Requirements

- Python 3.11 or newer
- The libraries in `requirements.txt` (versions are pinned)

## Setup

```
git clone https://github.com/k250076-glitch/paisapal.git
cd paisapal
pip install -r requirements.txt
```

## How to run

```
python src/main.py
```

Or open `src/main.py` in VS Code and press Run. The menu:

```
  1. Add an expense (the category is predicted for you)
  2. Add an expense in a foreign currency
  3. Add income
  4. Import transactions from a CSV file
  5. Set a monthly budget
  6. Monthly summary and budget check
  7. Draw charts
  8. Train and compare the two classifiers
  9. Exit
```

The first time, the app starts from the sample ledger in `data/raw`. Your data
is saved in `data/processed` after every change. Delete the files there to
start again from the sample data.

Every module can also be run on its own to see a short demo, for example
`python src/classifier.py` or `python src/plots.py`.

## How to run the tests

```
python -m unittest discover tests
```

There are 71 tests covering empty input, one element, duplicates, large input,
invalid input, missing files and no network. No internet is needed.

## Project layout

```
paisapal/
  src/
    main.py          menu (Polani)
    models.py        Transaction classes, Ledger, Budget (Polani)
    text_utils.py    text cleaning (Zain)
    classifier.py    TF-IDF, Naive Bayes, Logistic Regression, error analysis (Zain)
    data_io.py       CSV and JSON files, input checks (Nehal)
    api_client.py    exchange rates with a cache (Nehal)
    analysis.py      NumPy matrix and Pandas summary (Nehal)
    plots.py         charts (Nehal, confusion matrix by Zain)
  tests/             one test file per member
  data/raw/          training notes, hand-written test notes, sample ledger
  data/processed/    files the app saves while running (not in git)
  outputs/           charts and results the app creates (not in git)
  docs/DESIGN.md     design, data structures, algorithms and complexity
  docs/VIVA.md       viva questions with answers
```

## Results

| Model | Accuracy on the 20% test notes | Accuracy on 80 hand-written notes |
|---|---|---|
| Multinomial Naive Bayes (used by the app) | 0.997 | about 0.51 |
| Logistic Regression | 0.994 | |

The training notes come from templates, so the first score is very high. The
hand-written notes use new shops and new wording and show the real limits. See
`docs/DESIGN.md` sections 6.7 and 6.10.

## Data and privacy

The datasets were made by the group. They contain no names, phone numbers or
account details. The exchange-rate website (open.er-api.com) needs no API key,
so there are no secrets in the repository.

## More detail

- `docs/DESIGN.md`: how the program works, every data structure and algorithm,
  time and space complexity, testing, how to demo and who did what.
- `docs/VIVA.md`: likely viva questions with short answers.
