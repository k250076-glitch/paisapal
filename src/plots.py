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
the classifier knows. Part 11 fills in the confusion matrix; Part 12 the
other three charts.
"""

import os

import matplotlib

# "Agg" draws straight into files without opening a window, so the charts
# also work on a computer with no screen and never stop the program.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
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
    Time:   O(k)
    """
    raise NotImplementedError("Part 12")


def plot_monthly_trend(months, monthly_totals, path):
    """Line chart of total spending per month.

    Input:  months (list of "YYYY-MM"), monthly_totals (list or array of length m), path
    Output: path of the saved file
    Time:   O(m)
    """
    raise NotImplementedError("Part 12")


def plot_budget_vs_actual(categories, actual, limits, path):
    """Grouped bar chart: this month's spending next to the budget for each category.

    Input:  categories (list of str), actual and limits (lists of numbers), path
    Output: path of the saved file
    Time:   O(k)
    """
    raise NotImplementedError("Part 12")


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
