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

The Pandas functions are filled in by Part 9. n = number of records,
m = number of months, k = number of categories.

Run this file on its own (python src/analysis.py) to see a demo.
"""

import numpy as np


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
    raise NotImplementedError("Part 9")


def clean_dataframe(df):
    """Remove rows with a missing or non-number amount or date, and fill a missing
    category with "Other". Adds a "month" column. Time: O(n)
    """
    raise NotImplementedError("Part 9")


def monthly_summary(df):
    """Group expenses by month and category and return total, count and mean
    using groupby and agg. Time: O(n log n)
    """
    raise NotImplementedError("Part 9")


def top_spending_days(records, count=5):
    """Return the days with the most spending, sorted with a lambda. Time: O(n log n)"""
    raise NotImplementedError("Part 9")


def large_expenses(records, threshold):
    """Return the expenses above threshold using filter and a lambda. Time: O(n)"""
    raise NotImplementedError("Part 9")


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
