"""
test_data.py - tests for data_io.py, api_client.py, analysis.py and plots.py (owner: Nehal)

Run all tests from the project folder with:
    python -m unittest discover tests
or open this file in VS Code and press Run.

Edge cases covered: empty input, one row, duplicates, large input, invalid
input, a missing file and no network. The network is never really used: the
website is replaced by a fake (mock) so the tests also work offline.
"""

import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
import requests

# Let the tests import the modules in the src folder.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import api_client
from analysis import (build_month_matrix, clean_dataframe, large_expenses, matrix_summary,
                      monthly_summary, over_budget_mask, to_dataframe, top_spending_days)
from data_io import (InvalidTransactionError, parse_amount, parse_date, read_json,
                     read_ledger_csv, write_json, write_ledger_csv)
from plots import (plot_budget_vs_actual, plot_category_bar, plot_confusion_matrix,
                   plot_monthly_trend)

CATS = ("Food", "Transport", "Bills")
HEADER = "date,description,amount,currency,category,kind\n"


def record(day, amount, category="Food", currency="PKR", kind="expense"):
    """Make one record tuple for the tests."""
    return (day, "note", float(amount), currency, category, kind)


class FakeReply:
    """Pretends to be the reply from requests.get."""

    def __init__(self, status, data=None, bad_json=False):
        self.status_code = status
        self.data = data
        self.bad_json = bad_json

    def json(self):
        if self.bad_json:
            raise ValueError("not JSON")
        return self.data


class TempFolderTest(unittest.TestCase):
    """Gives every test its own empty folder, deleted afterwards."""

    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.folder)

    def write_file(self, name, text):
        path = os.path.join(self.folder, name)
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
        return path


class TestParsing(unittest.TestCase):
    """parse_amount and parse_date."""

    def test_good_amounts(self):
        self.assertEqual(parse_amount("850"), 850.0)
        self.assertEqual(parse_amount(" 1,200.50 "), 1200.5)
        self.assertEqual(parse_amount(99), 99.0)

    def test_bad_amounts(self):
        for bad in ["", "   ", "abc", "0", "-5", "nan", "inf", None]:
            with self.assertRaises(InvalidTransactionError):
                parse_amount(bad)

    def test_dates(self):
        self.assertEqual(parse_date(" 2026-11-03 "), "2026-11-03")
        self.assertEqual(parse_date("2028-02-29"), "2028-02-29")
        for bad in ["", "2026-02-30", "2026-13-01", "03-11-2026", "yesterday"]:
            with self.assertRaises(InvalidTransactionError):
                parse_date(bad)


class TestFiles(TempFolderTest):
    """Reading and writing CSV and JSON files."""

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            read_ledger_csv(os.path.join(self.folder, "nope.csv"))

    def test_empty_file_and_header_only(self):
        self.assertEqual(read_ledger_csv(self.write_file("empty.csv", "")), ([], 0))
        self.assertEqual(read_ledger_csv(self.write_file("header.csv", HEADER)), ([], 0))

    def test_one_row(self):
        path = self.write_file("one.csv", HEADER + "2026-11-03,biryani,850,pkr,Food,EXPENSE\n")
        records, skipped = read_ledger_csv(path)
        self.assertEqual(records, [("2026-11-03", "biryani", 850.0, "PKR", "Food", "expense")])
        self.assertEqual(skipped, 0)

    def test_bad_rows_are_skipped_and_counted(self):
        text = (HEADER + "2026-11-03,ok,850,PKR,Food,expense\n"
                + "2026-02-30,bad date,100,PKR,Food,expense\n"
                + "2026-11-03,bad amount,abc,PKR,Food,expense\n"
                + "2026-11-03,no category,100,PKR,,expense\n"
                + "2026-11-03,short row\n")
        records, skipped = read_ledger_csv(self.write_file("bad.csv", text))
        self.assertEqual(len(records), 1)
        self.assertEqual(skipped, 4)

    def test_duplicate_rows_are_kept(self):
        row = "2026-11-03,chai,100,PKR,Food,expense\n"
        records, skipped = read_ledger_csv(self.write_file("dup.csv", HEADER + row + row))
        self.assertEqual(len(records), 2)

    def test_large_file_round_trip(self):
        records = [record("2026-11-03", i + 1) for i in range(5000)]
        path = os.path.join(self.folder, "sub", "big.csv")
        write_ledger_csv(path, records)
        loaded, skipped = read_ledger_csv(path)
        self.assertEqual(loaded, records)
        self.assertEqual(skipped, 0)

    def test_json_round_trip_missing_and_broken(self):
        path = os.path.join(self.folder, "a", "b.json")
        write_json(path, {"Food": 1000})
        self.assertEqual(read_json(path), {"Food": 1000})
        self.assertEqual(read_json(os.path.join(self.folder, "nope.json"), default={}), {})
        broken = self.write_file("broken.json", "{not json")
        self.assertIsNone(read_json(broken))


class TestCurrency(TempFolderTest):
    """api_client with a fake website, so no real network is needed."""

    GOOD = FakeReply(200, {"result": "success", "rates": {"USD": 0.004, "AED": 0.0125}})

    def setUp(self):
        super().setUp()
        self.cache = os.path.join(self.folder, "rates_cache.json")

    def test_live_rates_are_inverted_and_cached(self):
        with mock.patch("requests.get", return_value=self.GOOD):
            rates, source = api_client.get_rates(self.cache)
        self.assertEqual(source, "live")
        self.assertEqual(rates["USD"], 250.0)
        self.assertEqual(read_json(self.cache)["rates"]["AED"], 80.0)

    def test_no_network_uses_the_cache(self):
        with mock.patch("requests.get", return_value=self.GOOD):
            api_client.get_rates(self.cache)
        with mock.patch("requests.get", side_effect=requests.exceptions.ConnectionError("offline")):
            amount, source = api_client.convert_to_pkr(10, "usd", self.cache)
        self.assertEqual((amount, source), (2500.0, "cache"))

    def test_no_network_and_no_cache_uses_fallback(self):
        with mock.patch("requests.get", side_effect=requests.exceptions.Timeout("slow")):
            rates, source = api_client.get_rates(self.cache)
        self.assertEqual(source, "fallback")
        self.assertEqual(rates, api_client.FALLBACK_RATES)

    def test_bad_replies_fall_back(self):
        for reply in [FakeReply(500), FakeReply(200, bad_json=True),
                      FakeReply(200, {"result": "error"})]:
            with mock.patch("requests.get", return_value=reply):
                rates, source = api_client.get_rates(self.cache)
            self.assertEqual(source, "fallback")

    def test_pkr_and_invalid_input(self):
        self.assertEqual(api_client.convert_to_pkr(500, "PKR", self.cache), (500.0, "none needed"))
        with self.assertRaises(InvalidTransactionError):
            api_client.convert_to_pkr(10, "XYZ", self.cache)
        with self.assertRaises(InvalidTransactionError):
            api_client.convert_to_pkr(-10, "USD", self.cache)


class TestAnalysis(unittest.TestCase):
    """The NumPy matrix, the Pandas summary and the lambda helpers."""

    def test_empty_records(self):
        months, matrix = build_month_matrix([], CATS)
        self.assertEqual(months, [])
        self.assertEqual(matrix.shape, (0, 3))
        self.assertEqual(list(matrix_summary(matrix)["total_per_category"]), [0, 0, 0])
        self.assertEqual(top_spending_days([]), [])

    def test_one_record(self):
        months, matrix = build_month_matrix([record("2026-11-03", 850)], CATS)
        self.assertEqual(months, ["2026-11"])
        self.assertEqual(matrix.tolist(), [[850.0, 0.0, 0.0]])

    def test_duplicates_add_up_in_one_cell(self):
        records = [record("2026-11-03", 100), record("2026-11-03", 100)]
        months, matrix = build_month_matrix(records, CATS)
        self.assertEqual(matrix[0, 0], 200)
        self.assertEqual(top_spending_days(records), [("2026-11-03", 200.0)])

    def test_income_foreign_and_unknown_category_are_ignored(self):
        records = [record("2026-11-03", 100), record("2026-11-03", 999, kind="income"),
                   record("2026-11-03", 50, currency="USD"), record("2026-11-03", 70, "Pets")]
        months, matrix = build_month_matrix(records, CATS)
        self.assertEqual(matrix.sum(), 100)

    def test_large_input_and_axis_sums(self):
        records = [record("2026-%02d-01" % (i % 12 + 1), 10, CATS[i % 3]) for i in range(36000)]
        months, matrix = build_month_matrix(records, CATS)
        self.assertEqual(matrix.shape, (12, 3))
        summary = matrix_summary(matrix)
        self.assertEqual(summary["total_per_category"].tolist(), [120000.0] * 3)
        self.assertEqual(summary["total_per_month"].sum(), 360000)

    def test_over_budget_mask_with_broadcasting(self):
        matrix = np.array([[100.0, 500.0, 50.0], [300.0, 100.0, 50.0]])
        mask = over_budget_mask(matrix, [200, 400, 0])
        # The 0 budget means "no limit", so the last column is never marked.
        self.assertEqual(mask.tolist(), [[False, True, False], [True, False, False]])

    def test_clean_dataframe_removes_bad_rows(self):
        records = [("2026-11-03", "ok", 100, "PKR", "Food", "expense"),
                   ("not a date", "bad", 100, "PKR", "Food", "expense"),
                   ("2026-11-03", "bad", "abc", "PKR", "Food", "expense"),
                   ("2026-11-03", "zero", 0, "PKR", "Food", "expense"),
                   ("2026-11-04", "no category", 50, "PKR", "", "expense")]
        df = clean_dataframe(to_dataframe(records))
        self.assertEqual(len(df), 2)
        self.assertEqual(list(df["category"]), ["Food", "Other"])
        self.assertEqual(list(df["month"]), ["2026-11", "2026-11"])

    def test_monthly_summary_totals(self):
        records = [record("2026-11-03", 100), record("2026-11-04", 300),
                   record("2026-11-05", 50, "Bills")]
        summary = monthly_summary(clean_dataframe(to_dataframe(records)))
        food = summary[summary["category"] == "Food"].iloc[0]
        self.assertEqual((food["total"], food["items"], food["average"]), (400, 2, 200))

    def test_large_expenses_filter(self):
        records = [record("2026-11-03", 100), record("2026-11-03", 9000),
                   record("2026-11-03", 9000, kind="income")]
        self.assertEqual(len(large_expenses(records, 8000)), 1)


class TestPlots(TempFolderTest):
    """Every chart is saved as a PNG file, also with empty data."""

    def test_all_charts_are_saved(self):
        paths = [
            plot_category_bar({"Food": 100, "Bills": 50}, os.path.join(self.folder, "f", "a.png")),
            plot_monthly_trend(["2026-10", "2026-11"], [100, 200], os.path.join(self.folder, "b.png")),
            plot_budget_vs_actual(["Food"], [100], [80], os.path.join(self.folder, "c.png")),
            plot_confusion_matrix(np.array([[2, 1], [0, 3]]), ["Food", "Bills"],
                                  os.path.join(self.folder, "d.png")),
        ]
        for path in paths:
            self.assertTrue(os.path.getsize(path) > 0)

    def test_empty_data_still_gives_a_chart(self):
        path = plot_category_bar({}, os.path.join(self.folder, "empty.png"))
        self.assertTrue(os.path.exists(path))
        path = plot_monthly_trend([], [], os.path.join(self.folder, "empty2.png"))
        self.assertTrue(os.path.exists(path))

    def test_lengths_must_match(self):
        with self.assertRaises(ValueError):
            plot_monthly_trend(["2026-11"], [1, 2], os.path.join(self.folder, "x.png"))
        with self.assertRaises(ValueError):
            plot_budget_vs_actual(["Food"], [1, 2], [3], os.path.join(self.folder, "y.png"))


if __name__ == "__main__":
    unittest.main()
