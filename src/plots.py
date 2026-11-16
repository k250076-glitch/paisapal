"""
plots.py - charts saved as PNG files in outputs/figures (owners: Nehal, Zain)

Each function draws one chart with a title, axis labels and units, saves it,
and closes it so memory is freed.

Agreed interface (filled in by Parts 11 and 12). k = number of categories,
m = number of months.
"""


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

    Input:  matrix (c x c array), labels (list of category names), path
    Output: path of the saved file
    Time:   O(c * c)
    """
    raise NotImplementedError("Part 11")
