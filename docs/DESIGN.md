# PaisaPal design document

This document grows with the project. Each part adds the section for the
code it builds, so it always matches what is in the repository.

Status: up to date with Parts 1 to 10.

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

## 5. Running each part on its own

Every module ends with an `if __name__ == "__main__":` block. Open the file in
VS Code and press Run (or `python src/models.py` and so on), and it prints a
short demo of that module. This block only runs when the file itself is run;
when another module imports the file, it is skipped.

## 5b. Why we agreed the interfaces first

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

### 6.4 Ledger and Budget (Part 5, models.py)

`Ledger` keeps every transaction in a **list**, in the order they were added.
A list fits because expenses arrive one after another, `append()` adds to the
end in O(1) time on average, and most questions ("total spent on Food in
October") need to look at every transaction anyway, which is O(n).

- `for_month("2026-10")` keeps the transactions whose date starts with that
  month, using a list comprehension.
- `total_by_category()` walks the list once and adds each expense to a dict
  `{category: total}`.
- `balance()` is the sum of `signed_amount()` over the list. This is where
  polymorphism pays off: no if statement is needed for income vs expense.
- `largest_expenses()` sorts with `key=lambda t: t.amount`, O(n log n).
- `from_records()` turns the tuples from `data_io` into objects. Rows in a
  foreign currency are skipped until Part 10 converts them, and rows that fail
  validation are skipped and counted.

`Budget` keeps the limits in a **dict** `{category: limit}`. Looking up the
limit of one category is O(1), because a dict uses hashing to jump straight to
the key. `check()` compares each limit with the amount spent and returns
"OK", "NEAR" (80% or more of the limit) or "OVER". The dict is private
(`self.__limits`), so limits can only be set through `set_limit()`, which
checks the category and the amount.

### 6.5 Train/test split and TF-IDF (Part 6, classifier.py)

`split_data()` keeps 80% of the notes for training and 20% for testing. The
split is random but uses a fixed seed (42), so every run and every member gets
the same split. `stratify=labels` keeps the same share of each category in
both parts, so a small category like Other is not missing from the test set.

TF-IDF turns each cleaned note into a row of numbers, one column per word or
word pair in the vocabulary:

- **TF (term frequency):** how often the word appears in this note. We use
  `1 + log(count)` (`sublinear_tf=True`) so a repeated word does not dominate.
- **IDF (inverse document frequency):** `log(n / number of notes containing
  the word)` (smoothed). A word that appears in almost every note gets a low
  IDF; a rare, specific word like "foodpanda" gets a high one.
- **TF-IDF = TF x IDF**, and each row is scaled to length 1.

We also use word pairs (`ngram_range=(1, 2)`), so "uni fee" is a feature as
well as "uni" and "fee". The vectorizer learns its vocabulary from the
training notes only (`fit_transform`); the test notes are only transformed.
If it learned from the test notes too, information about the test set would
leak into training and the accuracy would look better than it really is.

The result is a **sparse matrix**: about 1,300 columns, but each note uses
only 2 to 5 of them, so only the non-zero values are stored.

### 6.6 Monthly spending matrix (Part 7, analysis.py)

`build_month_matrix()` builds a **2-D NumPy array** with one row per month and
one column per category (6 x 8 for the sample ledger). Two dicts give the row
number of a month and the column number of a category in O(1), so each
record is added to its cell without searching.

Once the grid exists, NumPy does the rest without Python loops (vectorised):

- `matrix.sum(axis=0)`: total per category (down the columns).
- `matrix.sum(axis=1)`: total per month (across the rows).
- `matrix.mean(axis=0)`: average month for each category.
- `over_budget_mask()`: `matrix > budget_vector`. The budget has shape (8,) and
  the matrix (6, 8); **broadcasting** repeats the budget for every month and
  compares cell by cell, giving a True/False grid. A budget of 0 means no
  limit and is never marked.

Why NumPy instead of nested lists: the whole grid is stored as one block of
numbers, and operations like sum and comparison run in fast compiled code
instead of a Python loop per cell.

### 6.7 Two classifiers and how we compare them (Part 8, classifier.py)

`ExpenseClassifier` holds one TF-IDF vectorizer and one model. The model is
chosen by name: `"nb"` is Multinomial Naive Bayes (alpha=0.5 smoothing) and
`"lr"` is Logistic Regression (liblinear solver, one vs rest).

- `train()` cleans the notes, fits the vectorizer and fits the model.
- `predict()` cleans one note and returns a category. If nothing is left after
  cleaning it returns "Other". Predicting before training raises RuntimeError.
- `evaluate()` returns accuracy plus macro precision, recall and F1. Macro
  means the score is worked out per category and then averaged, so a small
  category counts as much as a big one.
- `compare_models()` splits the notes once, trains both models on the same
  80% and tests both on the same 20%, then keeps the one with the higher F1.
  A dict `{"nb": metrics, "lr": metrics}` holds the results.
- `save_correction()` appends (note, right category) to
  data/processed/corrections.csv. `load_training_data()` adds those rows to
  the dataset, so the next training learns from the user's corrections.

Results with seed 42:

| Model | Accuracy | Macro F1 |
|---|---|---|
| Multinomial Naive Bayes | 0.997 | about 0.997 |
| Logistic Regression | 0.994 | about 0.994 |

Honest limit: the 1,640 training notes come from templates, so the 20% test
notes look very like the training notes and the score is almost perfect. We
also wrote 80 notes by hand with new shops and new wording
(data/raw/expenses_hard_test.csv). On those the best model gets about 0.51
accuracy and 0.51 F1. This shows the model learns the words it has seen, not
the meaning, and that more varied real data is the main way to improve it.

### 6.8 Pandas summary and lambda helpers (Part 9, analysis.py)

- `to_dataframe()` turns record tuples into a DataFrame with named columns.
- `clean_dataframe()` uses `pd.to_numeric(..., errors="coerce")` and
  `pd.to_datetime(..., errors="coerce")` so a bad amount or date becomes
  missing (NaN or NaT) instead of crashing. Those rows are dropped, amounts of
  0 or less are dropped, an empty category becomes "Other" and a "month"
  column is added. On the raw sample CSV: 274 rows with 3 missing values
  become 271 clean rows.
- `monthly_summary()` uses `groupby(["month", "category"])` and
  `agg(["sum", "count", "mean"])` to give total, number of items and average
  for every month and category.
- `top_spending_days()` adds up spending per day in a dict, then sorts the
  (date, total) pairs with `sorted(..., key=lambda pair: pair[1])`.
- `large_expenses()` uses `filter` with a lambda; `amounts_in_thousands()`
  uses `map` with a lambda.

### 6.9 Currency conversion with a cache (Part 10, api_client.py)

`convert_to_pkr(amount, currency)` turns a foreign amount into rupees.
The rates come from a free website (open.er-api.com, no API key). We used it
instead of Frankfurter, which was in the plan, because Frankfurter has no PKR
rates. Rates are
looked for in this order:

1. "live": ask the website (5 second timeout) and save the answer to
   data/processed/rates_cache.json with the date.
2. "cache": if the website fails, use the last saved rates.
3. "fallback": if there is no cache either, use rough built-in rates. The app
   says so when it uses them.

Data structures: `SUPPORTED_CURRENCIES` is a set, so "is AED supported?" is
O(1). The rates are a dict {currency: rupees per 1 unit}.

Errors: no internet, a status that is not 200, a reply that is not JSON or a
reply without rates all become ConnectionError inside `fetch_rates()`, which
`get_rates()` catches before trying the cache. An unsupported currency or a
bad amount raises InvalidTransactionError. PKR is returned unchanged.

Testing: the lab network cannot reach the website, so we tested with a fake
(mocked) `requests.get` that returns a good reply, a 500 status, bad JSON, an
error reply and no connection, and checked that the source changes from live
to cache to fallback as expected. This is the part we planned to drop first
if we fell behind; the rest of the app works without it because foreign rows
are skipped.

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
| `Ledger.add()` | O(1) average | O(1) |
| `for_month()`, `total_by_category()`, `balance()` | O(n) | O(n) worst case for the result |
| `largest_expenses()` | O(n log n) | O(n) |
| `Budget.set_limit()`, `get_limit()` | O(1) average | O(k) for the dict |
| `Budget.check()` | O(k) | O(k) |
| `split_data()` | O(n) | O(n) |
| `build_features()` (TF-IDF), W words in total | O(W) | O(non-zero values), sparse |
| `build_month_matrix()`, m months, k categories | O(n + m*k) | O(m*k) |
| `over_budget_mask()`, `matrix_summary()` | O(m*k) | O(m*k) |
| `ExpenseClassifier.train()`, Naive Bayes | O(n * v) | O(v * c) |
| `ExpenseClassifier.train()`, Logistic Regression | O(r * n * v), r = passes | O(v * c) |
| `predict()` on one note of L characters | O(L + v * c) | O(L) |
| `evaluate()`, `compare_models()` | O(n * v * c) plus training | O(n) |
| `save_correction()` | O(1) | O(1) |
| `clean_dataframe()`, `to_dataframe()` | O(n) | O(n) |
| `monthly_summary()` (groupby) | O(n log n) | O(n) |
| `top_spending_days()` | O(n + d log d), d days | O(d) |
| `large_expenses()`, `amounts_in_thousands()` | O(n) | O(n) |
| `convert_to_pkr()`, c currencies | O(c) plus the network call | O(c) |