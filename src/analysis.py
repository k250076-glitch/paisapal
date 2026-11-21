"""
analysis.py - NumPy and Pandas analysis of spending (owner: Nehal)

The monthly spending matrix
    A 2-D NumPy array with one row per month and one column per category:

                 Food   Transport   Bills ...
        2026-06  9800   4200        5100
        2026-07  ...

    NumPy adds up a whole row or column in one step (no Python loop), and
    comparing the whole grid with the budget gives a grid of True/False
    showing which months went over budget.

n = number of records,
m = number of months, k = number of categories.

Run this file on its own (python src/analysis.py) to see a demo.
"""

import numpy as np
import pandas as pd

COLUMNS = ["date", "description", "amount", "currency", "category", "kind"]


def build_month_matrix(records, categories):
    """Build the months x categories spending matrix from expense records.

    Input:  records (list of record tuples), categories (tuple of str)
    Output: (months, matrix) where months is a sorted list of "YYYY-MM"
            and matrix is a NumPy array of shape (m, k)
    Time:   O(n + m * k)
    """
    # Keep only expenses in PKR. Foreign-currency rows are converted first
    # by the menu (Part 10) before they reach this function.
    expenses = [r for r in records if r[5] == "expense" and r[3] == "PKR"]

    # A sorted list of the different months, such as ["2026-06", "2026-07"].
    # A set removes repeats, then sorted() puts them in order.
    months = sorted({r[0][:7] for r in expenses})

    # Dicts that give the row number of a month and the column number of a
    # category in O(1), so we do not search the lists for every record.
    month_row = {month: i for i, month in enumerate(months)}
    category_col = {category: j for j, category in enumerate(categories)}

    # np.zeros makes a grid of m rows and k columns, all 0.0 at the start.
    matrix = np.zeros((len(months), len(categories)))
    for date, description, amount, currency, category, kind in expenses:
        if category in category_col:
            matrix[month_row[date[:7]], category_col[category]] += amount
    return months, matrix


def over_budget_mask(matrix, budget_vector):
    """Return a True/False matrix: True where spending is above the budget.

    The budget vector (one limit per category) is broadcast over every month.
    Input:  matrix (m x k array), budget_vector (array of length k)
    Output: boolean array of shape (m, k)
    Time:   O(m * k)
    """
    budget_vector = np.asarray(budget_vector, dtype=float)
    # Broadcasting: the budget has shape (k,) and the matrix (m, k). NumPy
    # repeats the budget row for every month, then compares cell by cell.
    # A budget of 0 means "no limit", so those cells are never marked.
    return (matrix > budget_vector) & (budget_vector > 0)


def matrix_summary(matrix):
    """Return totals and averages using NumPy along an axis.

    Output: dict with "total_per_category" (axis 0 sum), "total_per_month"
            (axis 1 sum) and "average_per_category" (axis 0 mean)
    Time:   O(m * k)
    """
    if matrix.size == 0:
        k = matrix.shape[1] if matrix.ndim == 2 else 0
        zeros = np.zeros(k)
        return {"total_per_category": zeros, "total_per_month": np.zeros(0),
                "average_per_category": zeros}
    # axis=0 works down the columns (one answer per category),
    # axis=1 works across the rows (one answer per month).
    return {
        "total_per_category": matrix.sum(axis=0),
        "total_per_month": matrix.sum(axis=1),
        "average_per_category": matrix.mean(axis=0),
    }


def to_dataframe(records):
    """Turn record tuples into a Pandas DataFrame. Time: O(n)"""
    return pd.DataFrame(records, columns=COLUMNS)


def clean_dataframe(df):
    """Remove rows with a missing or non-number amount or date, and fill a missing
    category with "Other". Adds a "month" column. Time: O(n)
    """
    df = df.copy()
    # to_numeric and to_datetime turn bad values such as "abc" into NaN or
    # NaT (Pandas' "missing"), instead of crashing.
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    df = df.dropna(subset=["amount", "date"])
    df = df[df["amount"] > 0]
    # An empty category ("") counts as missing too.
    df["category"] = df["category"].replace("", np.nan).fillna("Other")
    df["month"] = df["date"].dt.strftime("%Y-%m")
    return df.reset_index(drop=True)


def monthly_summary(df):
    """Group expenses by month and category and return total, count and mean
    using groupby and agg. Time: O(n log n)
    """
    expenses = df[(df["kind"] == "expense") & (df["currency"] == "PKR")]
    summary = expenses.groupby(["month", "category"])["amount"].agg(["sum", "count", "mean"])
    summary = summary.rename(columns={"sum": "total", "count": "items", "mean": "average"})
    return summary.round(0).reset_index()


def top_spending_days(records, count=5):
    """Return the days with the most spending, sorted with a lambda. Time: O(n log n)"""
    totals = {}
    for date, description, amount, currency, category, kind in records:
        if kind == "expense" and currency == "PKR":
            totals[date] = totals.get(date, 0) + amount
    # items() gives (date, total) pairs; the lambda sorts them by the total.
    ordered = sorted(totals.items(), key=lambda pair: pair[1], reverse=True)
    return ordered[:count]


def large_expenses(records, threshold):
    """Return the expenses above threshold using filter and a lambda. Time: O(n)"""
    return list(filter(lambda r: r[5] == "expense" and r[2] > threshold, records))


def amounts_in_thousands(records):
    """Return every amount divided by 1000, using map and a lambda. Time: O(n)"""
    return list(map(lambda r: round(r[2] / 1000, 1), records))


if __name__ == "__main__":
    # Demo: run this file on its own to see the NumPy matrix.
    import os
    from data_io import read_ledger_csv
    from models import CATEGORIES

    project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ledger_path = os.path.join(project_folder, "data", "raw", "ledger_sample.csv")

    records, skipped = read_ledger_csv(ledger_path)
    months, matrix = build_month_matrix(records, CATEGORIES)

    print("Demo of analysis.py: monthly spending matrix (Rs)")
    print()
    print("Month".ljust(9) + "".join(c[:9].rjust(10) for c in CATEGORIES))
    for month, row in zip(months, matrix):
        print(month.ljust(9) + "".join(format(value, ",.0f").rjust(10) for value in row))
    print()

    summary = matrix_summary(matrix)
    print("Total per month:   ", [format(v, ",.0f") for v in summary["total_per_month"]])
    print("Average per category:")
    for category, value in zip(CATEGORIES, summary["average_per_category"]):
        print(" ", category.ljust(14), format(value, ",.0f"))
    print()

    budget = np.array([15000, 15000, 15000, 15000, 8000, 7000, 8000, 5000])
    mask = over_budget_mask(matrix, budget)
    print("Over budget (budget broadcast over every month):")
    for i, month in enumerate(months):
        over = [CATEGORIES[j] for j in range(len(CATEGORIES)) if mask[i, j]]
        print(" ", month, ", ".join(over) if over else "none")
    print()

    raw_df = pd.read_csv(ledger_path)
    print("Pandas cleaning: the raw CSV has", len(raw_df), "rows and",
          int(raw_df.isna().sum().sum()), "missing values")
    df = clean_dataframe(raw_df)
    print("After clean_dataframe():", len(df), "rows (bad amounts and dates removed,",
          "missing category set to Other)")
    print()
    print("Pandas: monthly summary for 2026-11 (groupby month and category, then agg)")
    summary = monthly_summary(df)
    print(summary[summary["month"] == "2026-11"].to_string(index=False))
    print()

    print("Top 3 spending days (sorted with a lambda)")
    for date, total in top_spending_days(records, 3):
        print(" ", date, "Rs", format(total, ",.0f"))
    print()

    big = large_expenses(records, 8000)
    print("Expenses above Rs 8,000 (filter with a lambda):", len(big))
    for r in big[:3]:
        print(" ", r[0], r[4], "Rs", format(r[2], ",.0f"), r[1])

