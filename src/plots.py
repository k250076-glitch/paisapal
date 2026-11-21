"""
plots.py - charts saved as PNG files in outputs/figures (owners: Nehal, Zain)

Each function draws one chart with a title, axis labels and units, saves it,
and closes it so memory is freed.

Charts
    plot_category_bar       total spending per category (bar chart)
    plot_monthly_trend      total spending per month (line chart)
    plot_budget_vs_actual   spending next to the budget (grouped bar chart)
    plot_confusion_matrix   where the classifier goes wrong (heatmap, Zain)

k = number of categories, m = number of months, c = number of categories
the classifier knows. Run this file on its own to see a demo.
"""

import os

import matplotlib

# "Agg" draws straight into files without opening a window, so the charts
# also work on a computer with no screen and never stop the program.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def _save(figure, path):
    """Make the folder if needed, save the chart and close it. Time: O(1)"""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    figure.tight_layout()
    figure.savefig(path, dpi=120)
    # Closing frees the memory. Without it, many charts would pile up.
    plt.close(figure)
    return path


def plot_category_bar(totals, path):
    """Bar chart of total spending per category.

    Input:  totals (dict {category: amount}), path (str)
    Output: path of the saved file
    Time:   O(k log k) because the bars are sorted, biggest first
    """
    # Sort the (category, amount) pairs by amount with a lambda.
    pairs = sorted(totals.items(), key=lambda pair: pair[1], reverse=True)
    names = [pair[0] for pair in pairs]
    values = [pair[1] for pair in pairs]

    figure, axes = plt.subplots(figsize=(8, 4.5))
    axes.bar(names, values, color="steelblue")
    axes.set_title("Total spending per category")
    axes.set_xlabel("Category")
    axes.set_ylabel("Amount (Rs)")
    axes.tick_params(axis="x", rotation=30)
    if not names:
        axes.text(0.5, 0.5, "No expenses yet", ha="center", transform=axes.transAxes)
    return _save(figure, path)


def plot_monthly_trend(months, monthly_totals, path):
    """Line chart of total spending per month.

    Input:  months (list of "YYYY-MM"), monthly_totals (list or array of length m), path
    Output: path of the saved file
    Time:   O(m)
    """
    if len(months) != len(monthly_totals):
        raise ValueError("months and monthly_totals must have the same length")
    figure, axes = plt.subplots(figsize=(8, 4.5))
    axes.plot(months, monthly_totals, marker="o", color="darkorange")
    axes.set_title("Total spending per month")
    axes.set_xlabel("Month")
    axes.set_ylabel("Amount (Rs)")
    axes.grid(alpha=0.3)
    # Start the y axis at 0 so small changes do not look bigger than they are.
    axes.set_ylim(bottom=0)
    if len(months) == 0:
        axes.text(0.5, 0.5, "No expenses yet", ha="center", transform=axes.transAxes)
    return _save(figure, path)


def plot_budget_vs_actual(categories, actual, limits, path):
    """Grouped bar chart: this month's spending next to the budget for each category.

    Input:  categories (list of str), actual and limits (lists of numbers), path
    Output: path of the saved file
    Time:   O(k)
    """
    if not (len(categories) == len(actual) == len(limits)):
        raise ValueError("categories, actual and limits must have the same length")
    # np.arange gives the positions 0, 1, 2, ... for the groups. The two bars
    # of a group sit a little to the left and right of that position.
    positions = np.arange(len(categories))
    width = 0.4
    figure, axes = plt.subplots(figsize=(8, 4.5))
    axes.bar(positions - width / 2, actual, width, label="Spent", color="indianred")
    axes.bar(positions + width / 2, limits, width, label="Budget", color="seagreen")
    axes.set_xticks(positions)
    axes.set_xticklabels(categories, rotation=30)
    axes.set_title("Spending compared with the budget")
    axes.set_xlabel("Category")
    axes.set_ylabel("Amount (Rs)")
    axes.legend()
    return _save(figure, path)


def plot_confusion_matrix(matrix, labels, path):
    """Heatmap of the classifier's confusion matrix (owner: Zain).

    Rows are the true categories and columns the predicted ones. Dark cells on
    the diagonal are correct answers; any other number is a mistake.
    Input:  matrix (c x c array), labels (list of category names), path
    Output: path of the saved file
    Time:   O(c * c)
    """
    figure, axes = plt.subplots(figsize=(7, 6))
    # annot=True writes the number inside every cell, fmt="d" means whole numbers.
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=labels, yticklabels=labels, ax=axes)
    axes.set_title("Confusion matrix (rows: true, columns: predicted)")
    axes.set_xlabel("Predicted category")
    axes.set_ylabel("True category")
    return _save(figure, path)


if __name__ == "__main__":
    # Demo: run this file on its own to draw the three spending charts.
    from analysis import build_month_matrix
    from data_io import read_ledger_csv
    from models import CATEGORIES

    project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ledger_path = os.path.join(project_folder, "data", "raw", "ledger_sample.csv")
    figures = os.path.join(project_folder, "outputs", "figures")

    records, skipped = read_ledger_csv(ledger_path)
    months, matrix = build_month_matrix(records, CATEGORIES)

    print("Demo of plots.py: drawing three charts from the sample ledger")
    print()
    totals = dict(zip(CATEGORIES, matrix.sum(axis=0)))
    saved = [plot_category_bar(totals, os.path.join(figures, "category_bar.png")),
             plot_monthly_trend(months, matrix.sum(axis=1),
                                os.path.join(figures, "monthly_trend.png"))]
    limits = [15000, 15000, 15000, 15000, 8000, 7000, 8000, 5000]
    saved.append(plot_budget_vs_actual(list(CATEGORIES), list(matrix[-1]), limits,
                                       os.path.join(figures, "budget_vs_actual.png")))
    for path in saved:
        print("Saved", os.path.relpath(path, project_folder))
    print()
    print("Open the outputs/figures folder to see them.")
