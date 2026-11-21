"""
test_text_ml.py - tests for text_utils.py and classifier.py (owner: Zain)

Run all tests from the project folder with:
    python -m unittest discover tests
or open this file in VS Code and press Run.

Edge cases covered: empty input, one element, duplicates, large input and
invalid input. The classifier tests use a small hand-made dataset so they
run in a few seconds.
"""

import os
import shutil
import sys
import tempfile
import unittest

# Let the tests import the modules in the src folder.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from classifier import (ExpenseClassifier, compare_models, error_analysis, load_training_data,
                        save_correction, split_data)
from text_utils import STOP_WORDS, clean_many, clean_text

# A tiny dataset: 4 categories with 10 notes each.
SMALL_TEXTS = (["foodpanda biryani", "kfc burger", "pizza deal", "chai and samosa", "dhaba karahi",
                "mcdonalds fries", "biryani lunch", "burger dinner", "pizza slice", "karahi night"]
               + ["careem to uni", "uber ride", "indrive office", "petrol bike", "careem home",
                  "uber airport", "rickshaw ride", "petrol car", "bus fare", "indrive mall"]
               + ["k electric bill", "gas bill", "internet bill", "ptcl bill", "water bill",
                  "mobile package", "electric bill paid", "sui gas", "wifi bill", "jazz package"]
               + ["panadol dvago", "doctor fee", "medicine pharmacy", "clinic visit", "dvago syrup",
                  "lab test", "dentist", "panadol tablets", "eye drops", "pharmacy vitamins"])
SMALL_LABELS = ["Food"] * 10 + ["Transport"] * 10 + ["Bills"] * 10 + ["Health"] * 10


class TestCleanText(unittest.TestCase):
    """text_utils.clean_text and clean_many."""

    def test_empty_and_blank_notes(self):
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text("    "), "")
        self.assertEqual(clean_text("Rs 850 !!!"), "")

    def test_invalid_input_is_not_a_crash(self):
        self.assertEqual(clean_text(None), "")
        self.assertEqual(clean_text(123), "")

    def test_one_word(self):
        self.assertEqual(clean_text("FOODPANDA"), "foodpanda")

    def test_lowercase_and_symbols_removed(self):
        self.assertEqual(clean_text("KFC!!! Burger"), "kfc burger")

    def test_phrase_is_joined(self):
        self.assertEqual(clean_text("food panda biryani"), clean_text("foodpanda biryani"))

    def test_stop_words_are_removed(self):
        for word in clean_text("paid for the biryani at kfc").split():
            self.assertNotIn(word, STOP_WORDS)

    def test_duplicates_are_kept(self):
        self.assertEqual(clean_text("chai chai chai"), "chai chai chai")

    def test_large_input(self):
        note = "foodpanda biryani " * 5000
        self.assertEqual(len(clean_text(note).split()), 10000)

    def test_clean_many_keeps_order_and_length(self):
        notes = ["KFC", "", "careem to uni"]
        cleaned = clean_many(notes)
        self.assertEqual(len(cleaned), 3)
        self.assertEqual(cleaned[1], "")
        self.assertEqual(clean_many([]), [])


class TestSplit(unittest.TestCase):
    """classifier.split_data."""

    def test_split_sizes_and_same_result_every_time(self):
        first = split_data(SMALL_TEXTS, SMALL_LABELS)
        second = split_data(SMALL_TEXTS, SMALL_LABELS)
        self.assertEqual(len(first[0]), 32)
        self.assertEqual(len(first[1]), 8)
        self.assertEqual(first[1], second[1])

    def test_every_category_is_in_the_test_part(self):
        train_texts, test_texts, train_labels, test_labels = split_data(SMALL_TEXTS, SMALL_LABELS)
        self.assertEqual(set(test_labels), set(SMALL_LABELS))

    def test_different_lengths_are_rejected(self):
        with self.assertRaises(ValueError):
            split_data(["a", "b"], ["Food"])


class TestClassifier(unittest.TestCase):
    """ExpenseClassifier, compare_models, corrections and error analysis."""

    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.folder)

    def test_unknown_model_name_is_rejected(self):
        with self.assertRaises(ValueError):
            ExpenseClassifier("svm")

    def test_predict_before_training_is_an_error(self):
        with self.assertRaises(RuntimeError):
            ExpenseClassifier("nb").predict("kfc burger")

    def test_both_models_learn_the_small_dataset(self):
        for name in ("nb", "lr"):
            model = ExpenseClassifier(name)
            model.train(SMALL_TEXTS, SMALL_LABELS)
            self.assertEqual(model.predict("kfc biryani"), "Food")
            self.assertEqual(model.predict("careem ride"), "Transport")

    def test_empty_note_is_other(self):
        model = ExpenseClassifier("nb")
        model.train(SMALL_TEXTS, SMALL_LABELS)
        self.assertEqual(model.predict(""), "Other")
        self.assertEqual(model.predict("!!! 500"), "Other")

    def test_unseen_words_still_give_a_known_category(self):
        model = ExpenseClassifier("nb")
        model.train(SMALL_TEXTS, SMALL_LABELS)
        self.assertIn(model.predict("zzzz qqqq"), set(SMALL_LABELS))

    def test_evaluate_gives_scores_between_0_and_1(self):
        model = ExpenseClassifier("nb")
        model.train(SMALL_TEXTS, SMALL_LABELS)
        scores = model.evaluate(SMALL_TEXTS, SMALL_LABELS)
        for name in ("accuracy", "precision", "recall", "f1"):
            self.assertTrue(0 <= scores[name] <= 1)

    def test_compare_models_returns_both_and_the_best(self):
        results, best = compare_models(SMALL_TEXTS, SMALL_LABELS)
        self.assertEqual(set(results), {"nb", "lr"})
        best_f1 = max(results["nb"]["f1"], results["lr"]["f1"])
        self.assertEqual(results[best.model_name]["f1"], best_f1)

    def test_corrections_are_saved_with_one_header(self):
        path = os.path.join(self.folder, "corrections.csv")
        save_correction("shoe polish wala", "Other", path)
        save_correction("shoe polish wala", "Other", path)
        with open(path, encoding="utf-8") as file:
            lines = file.read().splitlines()
        self.assertEqual(lines, ["description,category", "shoe polish wala,Other",
                                 "shoe polish wala,Other"])

    def test_training_data_includes_corrections(self):
        dataset = os.path.join(self.folder, "data.csv")
        corrections = os.path.join(self.folder, "corrections.csv")
        with open(dataset, "w", encoding="utf-8") as file:
            file.write("description,category\nkfc burger,Food\n")
        texts, labels = load_training_data(dataset, corrections)
        self.assertEqual(len(texts), 1)
        save_correction("gola ganda", "Food", corrections)
        texts, labels = load_training_data(dataset, corrections)
        self.assertEqual(texts, ["kfc burger", "gola ganda"])

    def test_error_analysis_writes_only_wrong_predictions(self):
        model = ExpenseClassifier("nb")
        model.train(SMALL_TEXTS, SMALL_LABELS)
        texts = ["kfc burger", "careem ride", "kfc burger"]
        labels = ["Food", "Transport", "Health"]
        path = os.path.join(self.folder, "results", "wrong.csv")
        matrix, names = error_analysis(model, texts, labels, path)
        # Rows plus columns: every note is counted once.
        self.assertEqual(matrix.sum(), 3)
        # The diagonal holds the 2 right answers.
        self.assertEqual(sum(matrix[i][i] for i in range(len(names))), 2)
        with open(path, encoding="utf-8") as file:
            lines = file.read().splitlines()
        self.assertEqual(lines[1], "kfc burger,Health,Food")
        self.assertEqual(len(lines), 2)


if __name__ == "__main__":
    unittest.main()