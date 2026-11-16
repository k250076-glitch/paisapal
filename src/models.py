"""
models.py - the main classes of PaisaPal (owner: Polani)

Classes
    Transaction          abstract base class for any money movement
    ExpenseTransaction   money going out (inherits Transaction)
    IncomeTransaction    money coming in (inherits Transaction)
    Budget               monthly limit for each category, stored in a dict
    Ledger               every transaction, stored in a list

Agreed interface (filled in by Parts 2 and 5). n = number of transactions,
k = number of categories.
"""

from abc import ABC, abstractmethod

from data_io import InvalidTransactionError

# The categories the classifier can predict. A tuple, because the list of
# categories is fixed and should never be changed while the program runs.
CATEGORIES = ("Food", "Transport", "Bills", "Shopping",
              "Education", "Health", "Entertainment", "Other")


class Transaction(ABC):
    """One money movement. Cannot be created directly, only through a child class.

    Attributes: date (str YYYY-MM-DD), description (str), amount (private,
    always a positive float, checked by the setter), category (str).
    """

    def __init__(self, date, description, amount, category):
        """Store the values. The amount goes through the validated setter.

        Raises InvalidTransactionError for a bad amount. Time: O(1)
        """
        raise NotImplementedError("Part 2")

    @property
    def amount(self):
        """Return the private amount. Time: O(1)"""
        raise NotImplementedError("Part 2")

    @amount.setter
    def amount(self, value):
        """Set the amount only if it is a positive number.

        Raises InvalidTransactionError otherwise. Time: O(1)
        """
        raise NotImplementedError("Part 2")

    @abstractmethod
    def signed_amount(self):
        """Return the amount with a sign: negative for expenses, positive for income."""

    def describe(self):
        """Return a one-line description for printing. Time: O(1)"""
        raise NotImplementedError("Part 2")

    def to_record(self):
        """Return the transaction as a record tuple for saving.

        Output: (date, description, amount, "PKR", category, kind). Time: O(1)
        """
        raise NotImplementedError("Part 2")


class ExpenseTransaction(Transaction):
    """Money spent. signed_amount() is negative. Category must be in CATEGORIES."""

    def signed_amount(self):
        """Return -amount. Time: O(1)"""
        raise NotImplementedError("Part 2")

    def describe(self):
        """Return a line such as "2026-11-03  Food  Rs 850  foodpanda biryani". Time: O(1)"""
        raise NotImplementedError("Part 2")


class IncomeTransaction(Transaction):
    """Money received. signed_amount() is positive. Category is always "Income"."""

    def signed_amount(self):
        """Return +amount. Time: O(1)"""
        raise NotImplementedError("Part 2")

    def describe(self):
        """Return a line such as "2026-11-01  Income  Rs 30000  pocket money". Time: O(1)"""
        raise NotImplementedError("Part 2")


class Budget:
    """Monthly spending limit for each category.

    Stored in a dict {category: limit}, so finding the limit of one
    category is O(1).
    """

    def __init__(self):
        """Start with no limits. Time: O(1)"""
        raise NotImplementedError("Part 5")

    def set_limit(self, category, limit):
        """Set the monthly limit for a category.

        Raises InvalidTransactionError for an unknown category or a limit <= 0.
        Time: O(1)
        """
        raise NotImplementedError("Part 5")

    def get_limit(self, category):
        """Return the limit for a category, or None if no limit is set. Time: O(1)"""
        raise NotImplementedError("Part 5")

    def check(self, spent_by_category, warn_at=0.8):
        """Compare spending with the limits.

        Input:  spent_by_category (dict {category: amount spent this month}),
                warn_at (fraction of the limit that counts as "near", default 0.8)
        Output: list of tuples (category, spent, limit, status) where status is
                "OK", "NEAR" or "OVER"
        Time:   O(k)
        """
        raise NotImplementedError("Part 5")

    def to_dict(self):
        """Return a copy of the limits dict, used to save to JSON. Time: O(k)"""
        raise NotImplementedError("Part 5")

    @classmethod
    def from_dict(cls, data):
        """Build a Budget from a dict loaded from JSON. Time: O(k)"""
        raise NotImplementedError("Part 5")


class Ledger:
    """All transactions, stored in a list in the order they were added."""

    def __init__(self):
        """Start with an empty list. Time: O(1)"""
        raise NotImplementedError("Part 5")

    def add(self, transaction):
        """Add a transaction to the end of the list. Time: O(1) on average"""
        raise NotImplementedError("Part 5")

    def __len__(self):
        """Return how many transactions there are. Time: O(1)"""
        raise NotImplementedError("Part 5")

    def all(self):
        """Return the list of all transactions. Time: O(1)"""
        raise NotImplementedError("Part 5")

    def for_month(self, month):
        """Return transactions whose date starts with month ("YYYY-MM"). Time: O(n)"""
        raise NotImplementedError("Part 5")

    def total_by_category(self, month=None):
        """Add up expenses per category, for one month or for all time.

        Output: dict {category: total}. Time: O(n)
        """
        raise NotImplementedError("Part 5")

    def balance(self):
        """Return total income minus total expenses, using signed_amount(). Time: O(n)"""
        raise NotImplementedError("Part 5")

    def largest_expenses(self, count=5):
        """Return the biggest expenses, sorted with a lambda key. Time: O(n log n)"""
        raise NotImplementedError("Part 5")

    def to_records(self):
        """Return every transaction as a record tuple, for saving. Time: O(n)"""
        raise NotImplementedError("Part 5")
