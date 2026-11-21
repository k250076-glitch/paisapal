"""
main.py - the console menu of PaisaPal (owner: Polani)

Run it from VS Code with the Run button, or from the project folder with:
    python src/main.py

This file joins all the modules together:
    models.py      Transaction classes, Ledger (a list) and Budget (a dict)
    classifier.py  predicts the category of a note
    api_client.py  converts foreign money to PKR
    analysis.py    NumPy matrix and Pandas summary
    plots.py       charts saved to outputs/figures
    data_io.py     reading and saving files

Where the data is kept
    data/processed/ledger.csv       every transaction (saved after each change)
    data/processed/budget.json      the monthly limits
    data/processed/corrections.csv  categories the user corrected
The first time, the ledger starts from data/raw/ledger_sample.csv so there
is something to look at.
"""

import os
from datetime import date

from analysis import build_month_matrix, clean_dataframe, monthly_summary, to_dataframe
from api_client import SUPPORTED_CURRENCIES, get_rates
from classifier import (ExpenseClassifier, compare_models, load_training_data,
                        save_correction)
from data_io import (InvalidTransactionError, parse_amount, parse_date, read_json,
                     read_ledger_csv, write_json, write_ledger_csv)
from models import CATEGORIES, Budget, ExpenseTransaction, IncomeTransaction, Ledger
from plots import plot_budget_vs_actual, plot_category_bar, plot_monthly_trend

# Folder of this file (src) and the project folder above it.
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SRC_DIR)

DATASET_PATH = os.path.join(PROJECT_DIR, "data", "raw", "expenses_labelled.csv")
SAMPLE_LEDGER_PATH = os.path.join(PROJECT_DIR, "data", "raw", "ledger_sample.csv")
LEDGER_PATH = os.path.join(PROJECT_DIR, "data", "processed", "ledger.csv")
BUDGET_PATH = os.path.join(PROJECT_DIR, "data", "processed", "budget.json")
CORRECTIONS_PATH = os.path.join(PROJECT_DIR, "data", "processed", "corrections.csv")
FIGURES_DIR = os.path.join(PROJECT_DIR, "outputs", "figures")

MENU = """
PaisaPal main menu
  1. Add an expense (the category is predicted for you)
  2. Add an expense in a foreign currency
  3. Add income
  4. Import transactions from a CSV file
  5. Set a monthly budget
  6. Monthly summary and budget check
  7. Draw charts
  8. Train and compare the two classifiers
  9. Exit
"""


# Small input helpers. Each one keeps asking until the answer is valid, so a
# typing mistake never crashes the program.

def ask_text(prompt):
    """Ask until the user types something that is not empty. Time: O(L)"""
    while True:
        answer = input(prompt).strip()
        if answer:
            return answer
        print("  Please type something.")


def ask_amount(prompt):
    """Ask until the user types a positive number. Returns a float."""
    while True:
        try:
            return parse_amount(input(prompt))
        except InvalidTransactionError as error:
            print("  " + str(error))


def ask_date(prompt):
    """Ask for a date. Pressing Enter gives today's date."""
    while True:
        answer = input(prompt).strip()
        if answer == "":
            return date.today().isoformat()
        try:
            return parse_date(answer)
        except InvalidTransactionError as error:
            print("  " + str(error))


def ask_category(prompt, allow_blank=False):
    """Show the numbered categories and ask for one.

    With allow_blank=True, pressing Enter returns None (keep the guess).
    """
    for number, category in enumerate(CATEGORIES, start=1):
        print("   ", number, category)
    while True:
        answer = input(prompt).strip()
        if answer == "" and allow_blank:
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(CATEGORIES):
            return CATEGORIES[int(answer) - 1]
        print("  Type a number from 1 to", len(CATEGORIES))


def ask_month(prompt, ledger):
    """Ask for a month "YYYY-MM". Enter gives the latest month in the ledger."""
    months = sorted({t.date[:7] for t in ledger.all()})
    default = months[-1] if months else date.today().isoformat()[:7]
    while True:
        answer = input(prompt + " [" + default + "]: ").strip()
        if answer == "":
            return default
        try:
            # Adding "-01" lets parse_date check the year and month for us.
            return parse_date(answer + "-01")[:7]
        except InvalidTransactionError:
            print("  Month must look like 2026-11")


# Loading and saving

def convert_records(records):
    """Turn foreign-currency records into PKR records, using one set of rates.

    Output: (converted records, number that could not be converted, rates source)
    Time:   O(n + c)
    """
    foreign = [r for r in records if r[3] != "PKR"]
    if not foreign:
        return records, 0, "none needed"
    # get_rates() is called once, not once per row, so we wait for the
    # website at most one time.
    rates, source = get_rates()
    converted = []
    failed = 0
    for day, description, amount, currency, category, kind in records:
        if currency == "PKR":
            converted.append((day, description, amount, currency, category, kind))
        elif currency in rates:
            pkr = round(amount * rates[currency], 2)
            converted.append((day, description + " (" + format(amount, "g") + " " + currency + ")",
                              pkr, "PKR", category, kind))
        else:
            failed += 1
    return converted, failed, source


def load_ledger():
    """Load the saved ledger, or the sample ledger the first time.

    Output: Ledger. Time: O(n)
    """
    if os.path.exists(LEDGER_PATH):
        path = LEDGER_PATH
    else:
        path = SAMPLE_LEDGER_PATH
        print("First run: starting from the sample ledger.")
    try:
        records, bad_rows = read_ledger_csv(path)
    except FileNotFoundError:
        print("No ledger file found, starting with an empty ledger.")
        return Ledger()
    records, failed, source = convert_records(records)
    ledger, skipped = Ledger.from_records(records)
    print("Loaded", len(ledger), "transactions.", bad_rows + failed + skipped, "bad rows were skipped.")
    if source != "none needed":
        print("Foreign amounts were converted using", source, "rates.")
    return ledger


def save_all(ledger, budget):
    """Save the ledger to CSV and the budget to JSON. Time: O(n + k)"""
    write_ledger_csv(LEDGER_PATH, ledger.to_records())
    write_json(BUDGET_PATH, budget.to_dict())


def train_classifier():
    """Train Naive Bayes on the dataset plus saved corrections. Time: O(n * v)"""
    texts, labels = load_training_data(DATASET_PATH, CORRECTIONS_PATH)
    classifier = ExpenseClassifier("nb")
    classifier.train(texts, labels)
    return classifier


# One function for each menu option

def budget_alert(ledger, budget, category, month):
    """Print a warning if a category is near or over its limit this month."""
    for name, spent, limit, status in budget.check(ledger.total_by_category(month)):
        if name == category and status != "OK":
            print("  Budget alert:", name, "is", status, "- spent Rs", format(spent, ",.0f"),
                  "of Rs", format(limit, ",.0f"), "this month.")


def add_expense(ledger, budget, classifier, foreign=False):
    """Menu 1 and 2: add an expense with a predicted category the user can correct."""
    note = ask_text("What did you spend on? (for example: foodpanda biryani): ")
    if foreign:
        print("  Supported currencies:", ", ".join(sorted(SUPPORTED_CURRENCIES)))
        while True:
            currency = input("Currency: ").strip().upper()
            if currency in SUPPORTED_CURRENCIES:
                break
            print("  Currency not supported.")
        original = ask_amount("Amount in " + currency + ": ")
        rates, source = get_rates()
        if currency not in rates:
            print("  No rate available for", currency, "- expense not added.")
            return
        amount = round(original * rates[currency], 2)
        print("  ", original, currency, "= Rs", format(amount, ",.2f"), "(" + source + " rate)")
        note = note + " (" + format(original, "g") + " " + currency + ")"
    else:
        amount = ask_amount("Amount in Rs: ")

    guess = classifier.predict(note)
    print("  Predicted category:", guess)
    choice = ask_category("Press Enter to accept, or type the number of the right category: ",
                          allow_blank=True)
    category = guess if choice is None else choice
    if choice is not None and choice != guess:
        # Remember the correction so the model learns it next time it trains.
        save_correction(note, choice, CORRECTIONS_PATH)
        print("  Thanks, the correction was saved for the next training.")
    if category not in CATEGORIES:
        category = "Other"
    day = ask_date("Date YYYY-MM-DD (Enter for today): ")

    ledger.add(ExpenseTransaction(day, note, amount, category))
    save_all(ledger, budget)
    print("  Added:", ledger.all()[-1].describe())
    budget_alert(ledger, budget, category, day[:7])


def add_income(ledger, budget):
    """Menu 3: add income."""
    note = ask_text("Where is the money from? (for example: pocket money): ")
    amount = ask_amount("Amount in Rs: ")
    day = ask_date("Date YYYY-MM-DD (Enter for today): ")
    ledger.add(IncomeTransaction(day, note, amount))
    save_all(ledger, budget)
    print("  Added:", ledger.all()[-1].describe())


def import_csv(ledger, budget):
    """Menu 4: add every good row of a CSV file to the ledger."""
    path = ask_text("Path of the CSV file (columns date,description,amount,currency,category,kind): ")
    path = path.strip('"')
    try:
        records, bad_rows = read_ledger_csv(path)
    except FileNotFoundError:
        print("  File not found:", path)
        return
    except (OSError, UnicodeDecodeError) as error:
        print("  Could not read the file:", error)
        return
    records, failed, source = convert_records(records)
    new_items, skipped = Ledger.from_records(records)
    for transaction in new_items.all():
        ledger.add(transaction)
    save_all(ledger, budget)
    print("  Imported", len(new_items), "transactions,", bad_rows + failed + skipped, "rows skipped.")


def set_budget(ledger, budget):
    """Menu 5: set the monthly limit of one category."""
    category = ask_category("Category number: ")
    current = budget.get_limit(category)
    if current is not None:
        print("  Current limit: Rs", format(current, ",.0f"))
    limit = ask_amount("New monthly limit in Rs: ")
    budget.set_limit(category, limit)
    save_all(ledger, budget)
    print("  Limit for", category, "set to Rs", format(limit, ",.0f"))


def monthly_report(ledger, budget):
    """Menu 6: totals, budget check, balance and biggest expenses for one month."""
    if len(ledger) == 0:
        print("  The ledger is empty. Add an expense first.")
        return
    month = ask_month("Month", ledger)
    totals = ledger.total_by_category(month)
    print()
    print("Spending in", month)
    if not totals:
        print("  No expenses in this month.")
    for category in CATEGORIES:
        if category in totals:
            print("  " + category.ljust(14), "Rs", format(totals[category], ",.0f").rjust(10))
    print("  " + "Total".ljust(14), "Rs", format(sum(totals.values()), ",.0f").rjust(10))

    report = budget.check(totals)
    print()
    if report:
        print("Budget check")
        for category, spent, limit, status in report:
            print("  " + category.ljust(14), format(spent, ",.0f").rjust(10), "of",
                  format(limit, ",.0f").rjust(10), " ", status)
    else:
        print("No budgets set yet (menu option 5).")

    # Pandas: number of items and average per category for this month.
    df = clean_dataframe(to_dataframe(ledger.to_records()))
    summary = monthly_summary(df)
    summary = summary[summary["month"] == month]
    if len(summary) > 0:
        print()
        print("Items and average per category (Pandas groupby)")
        print(summary[["category", "items", "average"]].to_string(index=False))

    print()
    print("Balance of the whole ledger (income minus expenses): Rs", format(ledger.balance(), ",.0f"))
    print("Three biggest expenses ever:")
    for transaction in ledger.largest_expenses(3):
        print("  " + transaction.describe())


def draw_charts(ledger, budget):
    """Menu 7: draw the three spending charts and open the folder."""
    records = ledger.to_records()
    months, matrix = build_month_matrix(records, CATEGORIES)
    if len(months) == 0:
        print("  No expenses yet, so there is nothing to draw.")
        return
    totals = dict(zip(CATEGORIES, matrix.sum(axis=0)))
    limits = [budget.get_limit(c) or 0 for c in CATEGORIES]
    saved = [
        plot_category_bar(totals, os.path.join(FIGURES_DIR, "category_bar.png")),
        plot_monthly_trend(months, matrix.sum(axis=1), os.path.join(FIGURES_DIR, "monthly_trend.png")),
        plot_budget_vs_actual(list(CATEGORIES), list(matrix[-1]), limits,
                              os.path.join(FIGURES_DIR, "budget_vs_actual.png")),
    ]
    for path in saved:
        print("  Saved", os.path.relpath(path, PROJECT_DIR))
    print("  The budget chart is for", months[-1] + ".")
    # On Windows, open the folder so the charts can be shown straight away.
    if hasattr(os, "startfile"):
        try:
            os.startfile(FIGURES_DIR)
        except OSError:
            pass


def compare_classifiers():
    """Menu 8: train both models on the same split, print the table, return the best."""
    print("  Training both models, please wait...")
    texts, labels = load_training_data(DATASET_PATH, CORRECTIONS_PATH)
    results, best = compare_models(texts, labels)
    print()
    print("  " + "Model".ljust(26) + "Accuracy  Precision  Recall    F1")
    for name, metrics in results.items():
        print("  " + ExpenseClassifier.MODEL_NAMES[name].ljust(26)
              + format(metrics["accuracy"], ".3f").ljust(10)
              + format(metrics["precision"], ".3f").ljust(11)
              + format(metrics["recall"], ".3f").ljust(10)
              + format(metrics["f1"], ".3f"))
    print()
    print("  From now on the app uses:", best.full_name())
    return best


def main():
    """Load everything, then show the menu until the user chooses Exit."""
    print("PaisaPal - Smart Expense Categorizer and Budget Planner")
    print()
    ledger = load_ledger()
    budget = Budget.from_dict(read_json(BUDGET_PATH, default={}) or {})
    print("Training the category model...")
    classifier = train_classifier()
    print("Ready.")

    while True:
        print(MENU)
        try:
            choice = input("Choose 1-9: ").strip()
        except EOFError:
            # The input ended (for example Ctrl+Z on Windows), so stop cleanly.
            choice = "9"
        try:
            if choice == "1":
                add_expense(ledger, budget, classifier)
            elif choice == "2":
                add_expense(ledger, budget, classifier, foreign=True)
            elif choice == "3":
                add_income(ledger, budget)
            elif choice == "4":
                import_csv(ledger, budget)
            elif choice == "5":
                set_budget(ledger, budget)
            elif choice == "6":
                monthly_report(ledger, budget)
            elif choice == "7":
                draw_charts(ledger, budget)
            elif choice == "8":
                classifier = compare_classifiers()
            elif choice == "9":
                save_all(ledger, budget)
                print("Saved. Goodbye!")
                break
            else:
                print("Please type a number from 1 to 9.")
        except InvalidTransactionError as error:
            print("  Not saved:", error)
        except EOFError:
            save_all(ledger, budget)
            print()
            print("Input ended. Saved. Goodbye!")
            break


if __name__ == "__main__":
    main()
