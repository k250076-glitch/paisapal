# PaisaPal design document

This document grows with the project. Each part adds the section for the
code it builds, so it always matches what is in the repository.

Status: up to date with Parts 1 to 4.

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

### 6.1 Transaction classes (Part 2, models.py)

`Transaction` is an abstract base class (ABC). It holds what every money
movement has: a date, a description, an amount and a category. It cannot be
created on its own, because two of its methods, `signed_amount()` and
`kind()`, are abstract: they have no body and each child class must write
its own.

- `ExpenseTransaction` returns `-amount` and checks that the category is one
  of the 8 in `CATEGORIES`.
- `IncomeTransaction` returns `+amount` and always uses the category "Income".

This is inheritance (the children reuse the constructor, `amount` and
`to_record()`) and overriding (each child writes its own `signed_amount()`
and `describe()`). It gives polymorphism: a loop over a mixed list can call
`t.signed_amount()` on every item and Python runs the right version for
each one, so the balance is just the sum of signed amounts.

Encapsulation: the amount is stored as `self.__amount`. The two underscores
make Python hide it from outside code, so the only way to change it is the
`amount` setter, which calls `parse_amount()` and rejects zero, negative or
non-number values with `InvalidTransactionError`.

`CATEGORIES` is a tuple, because the list of categories is fixed and must not
be changed while the program runs.

### 6.2 Text cleaning (Part 3, text_utils.py)

`clean_text()` turns "Rs 850 FOODPANDA biryani!!" into "foodpanda biryani"
in five steps:

1. Lowercase everything, so "Uber" and "uber" are the same word.
2. Replace every character that is not a letter or space with a space. This
   removes digits, amounts and symbols in one step.
3. Join two-word names with `PHRASE_MAP` (a dict), for example
   "food panda" -> "foodpanda", so the name is one feature.
4. Replace short forms and misspellings with `NORMALISE_MAP` (a dict), for
   example "fp" -> "foodpanda" and "biriyani" -> "biryani".
5. Drop every word that is in `STOP_WORDS` (a set) or is one letter long.

Why a set for stop-words: we ask "is this word a stop-word?" once for every
word of every note. A set answers in O(1) time on average, because it uses
hashing to jump straight to where the word would be. A list would have to
check every stop-word one by one, O(s).

Why dicts for the maps: we look up "what is the standard form of this word?",
which a dict also answers in O(1) using hashing.

Payment apps (JazzCash, Easypaisa) and money words (rs, pkr) are stop-words
because they appear in every category and only confuse the classifier.

`clean_many()` cleans a whole list with a list comprehension, and
`log_cleaning()` writes "original -> cleaned" lines to a TXT file so we can
check the cleaning by eye.

### 6.3 File input and output (Part 4, data_io.py)

All file reading and writing is in one module, so every file error is handled
in one place.

- `read_ledger_csv()` reads the ledger with `csv.DictReader`. Each good row
  becomes a tuple `(date, description, amount, currency, category, kind)`. A
  tuple is used because a saved record should not change by accident.
- Bad rows (missing or non-number amount, impossible date, missing category,
  too few columns) are skipped and counted instead of crashing the program.
  The sample ledger has 4 bad rows on purpose, and all 4 are skipped.
- `parse_amount()` and `parse_date()` check input and raise our custom
  exception `InvalidTransactionError` with a clear message. They are also used
  by the Transaction classes and, later, the menu.
- `read_json()` returns a default value if the file is missing or broken, so
  the app can start the first time when no budget or cache file exists yet.
- Only specific exceptions are caught (`FileNotFoundError`,
  `json.JSONDecodeError`, `InvalidTransactionError`, `KeyError`), never a bare
  `except`, so real bugs are not hidden.

## 7. Time and space complexity of the main operations

Filled in as each part is built.

| Operation | Time | Space |
|---|---|---|
| Create a transaction (validate date and amount) | O(1) | O(1) |
| `signed_amount()`, `describe()`, `to_record()` | O(1) | O(1) |
| `clean_text()` on one note of L characters | O(L) | O(L) |
| Stop-word or normalisation lookup (set or dict) | O(1) average | O(s) for the whole set |
| `clean_many()` on all notes, N characters in total | O(N) | O(N) |
| `parse_amount()`, `parse_date()` | O(1) for short input | O(1) |
| `read_ledger_csv()`, `write_ledger_csv()`, n rows | O(n) | O(n) |
| `load_labelled_dataset()`, n rows | O(n) | O(n) |
