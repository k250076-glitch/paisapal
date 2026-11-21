"""
test_core.py - tests for models.py (owner: Polani)

Run all tests from the project folder with:
    python -m unittest discover tests
or open this file in VS Code and press Run.

Edge cases covered: empty input, one element, duplicates, large input and
invalid input.
"""

import os
import sys
import unittest

# Let the tests import the modules in the src folder.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from data_io import InvalidTransactionError
from models import (CATEGORIES, Budget, ExpenseTransaction, IncomeTransaction, Ledger,
                    Transaction)


class TestTransactions(unittest.TestCase):
    """The Transaction classes: validation, inheritance and polymorphism."""

    def test_expense_is_negative_and_income_is_positive(self):
        expense = ExpenseTransaction("2026-11-03", "foodpanda biryani", 850, "Food")
        income = IncomeTransaction("2026-11-01", "pocket money", 30000)
        self.assertEqual(expense.signed_amount(), -850)
        self.assertEqual(income.signed_amount(), 30000)
        self.assertEqual(expense.kind(), "expense")
        self.assertEqual(income.category, "Income")

    def test_describe_is_different_for_each_class(self):
        expense = ExpenseTransaction("2026-11-03", "biryani", 850, "Food")
        income = IncomeTransaction("2026-11-01", "pocket money", 30000)
        self.assertTrue(expense.describe().startswith("[spent]"))
        self.assertTrue(income.describe().startswith("[received]"))

    def test_abstract_class_cannot_be_created(self):
        with self.assertRaises(TypeError):
            Transaction("2026-11-03", "x", 100, "Food")

    def test_amount_text_with_comma_is_accepted(self):
        expense = ExpenseTransaction("2026-11-03", "laptop bag", "1,200.50", "Shopping")
        self.assertEqual(expense.amount, 1200.5)

    def test_invalid_amounts_are_rejected(self):
        for bad in [0, -100, "", "abc", "nan", None]:
            with self.assertRaises(InvalidTransactionError):
                ExpenseTransaction("2026-11-03", "x", bad, "Food")

    def test_setter_also_checks_later_changes(self):
        expense = ExpenseTransaction("2026-11-03", "x", 100, "Food")
        with self.assertRaises(InvalidTransactionError):
            expense.amount = -5
        self.assertEqual(expense.amount, 100)

    def test_invalid_date_and_category_are_rejected(self):
        with self.assertRaises(InvalidTransactionError):
            ExpenseTransaction("2026-02-30", "x", 100, "Food")
        with self.assertRaises(InvalidTransactionError):
            ExpenseTransaction("03/11/2026", "x", 100, "Food")
        with self.assertRaises(InvalidTransactionError):
            ExpenseTransaction("2026-11-03", "x", 100, "Pets")

    def test_to_record_gives_a_tuple(self):
        expense = ExpenseTransaction("2026-11-03", "biryani", 850, "Food")
        self.assertEqual(expense.to_record(), ("2026-11-03", "biryani", 850.0, "PKR", "Food", "expense"))


class TestLedger(unittest.TestCase):
    """The Ledger list."""

    def test_empty_ledger(self):
        ledger = Ledger()
        self.assertEqual(len(ledger), 0)
        self.assertEqual(ledger.balance(), 0)
        self.assertEqual(ledger.total_by_category(), {})
        self.assertEqual(ledger.largest_expenses(), [])
        self.assertEqual(ledger.for_month("2026-11"), [])

    def test_one_transaction(self):
        ledger = Ledger()
        ledger.add(ExpenseTransaction("2026-11-03", "biryani", 850, "Food"))
        self.assertEqual(len(ledger), 1)
        self.assertEqual(ledger.balance(), -850)
        self.assertEqual(ledger.total_by_category("2026-11"), {"Food": 850})
        self.assertEqual(ledger.total_by_category("2026-10"), {})

    def test_duplicates_are_both_kept_and_added_up(self):
        ledger = Ledger()
        for _ in range(2):
            ledger.add(ExpenseTransaction("2026-11-03", "chai", 100, "Food"))
        self.assertEqual(len(ledger), 2)
        self.assertEqual(ledger.total_by_category(), {"Food": 200})

    def test_large_ledger(self):
        ledger = Ledger()
        for i in range(10000):
            ledger.add(ExpenseTransaction("2026-11-03", "item", i + 1, CATEGORIES[i % 8]))
        self.assertEqual(len(ledger), 10000)
        self.assertEqual(ledger.balance(), -sum(range(1, 10001)))
        biggest = ledger.largest_expenses(3)
        self.assertEqual([t.amount for t in biggest], [10000, 9999, 9998])

    def test_only_transactions_can_be_added(self):
        with self.assertRaises(InvalidTransactionError):
            Ledger().add(("2026-11-03", "x", 100))

    def test_balance_uses_income_and_expenses(self):
        ledger = Ledger()
        ledger.add(IncomeTransaction("2026-11-01", "pocket money", 30000))
        ledger.add(ExpenseTransaction("2026-11-03", "biryani", 850, "Food"))
        self.assertEqual(ledger.balance(), 29150)
        # Income is not counted as spending.
        self.assertEqual(ledger.total_by_category(), {"Food": 850})

    def test_from_records_skips_foreign_and_bad_rows(self):
        records = [("2026-11-03", "biryani", 850.0, "PKR", "Food", "expense"),
                   ("2026-11-03", "book", 20.0, "USD", "Education", "expense"),
                   ("2026-11-03", "pet food", 500.0, "PKR", "Pets", "expense"),
                   ("2026-11-01", "salary", 5000.0, "PKR", "Income", "income")]
        ledger, skipped = Ledger.from_records(records)
        self.assertEqual(len(ledger), 2)
        self.assertEqual(skipped, 2)

    def test_from_records_with_empty_list(self):
        ledger, skipped = Ledger.from_records([])
        self.assertEqual((len(ledger), skipped), (0, 0))


class TestBudget(unittest.TestCase):
    """The Budget dict."""

    def test_ok_near_and_over(self):
        budget = Budget()
        budget.set_limit("Food", 1000)
        budget.set_limit("Transport", 1000)
        budget.set_limit("Bills", 1000)
        report = budget.check({"Food": 500, "Transport": 850, "Bills": 1200})
        statuses = {category: status for category, spent, limit, status in report}
        self.assertEqual(statuses, {"Food": "OK", "Transport": "NEAR", "Bills": "OVER"})

    def test_exactly_at_the_limit_is_near_not_over(self):
        budget = Budget()
        budget.set_limit("Food", 1000)
        self.assertEqual(budget.check({"Food": 1000})[0][3], "NEAR")

    def test_empty_budget_and_no_spending(self):
        self.assertEqual(Budget().check({}), [])
        budget = Budget()
        budget.set_limit("Food", 1000)
        self.assertEqual(budget.check({}), [("Food", 0, 1000.0, "OK")])

    def test_setting_the_same_category_twice_keeps_the_last(self):
        budget = Budget()
        budget.set_limit("Food", 1000)
        budget.set_limit("Food", 2000)
        self.assertEqual(budget.get_limit("Food"), 2000)
        self.assertEqual(len(budget.to_dict()), 1)

    def test_invalid_limits_are_rejected(self):
        budget = Budget()
        with self.assertRaises(InvalidTransactionError):
            budget.set_limit("Pets", 1000)
        with self.assertRaises(InvalidTransactionError):
            budget.set_limit("Food", -1)
        self.assertIsNone(budget.get_limit("Food"))

    def test_save_and_load_round_trip_skips_bad_entries(self):
        budget = Budget.from_dict({"Food": 1000, "Pets": 50, "Bills": "abc"})
        self.assertEqual(budget.to_dict(), {"Food": 1000.0})


if __name__ == "__main__":
    unittest.main()
