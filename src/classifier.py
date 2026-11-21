"""
classifier.py - predicting the category of an expense (owner: Zain)

How it works
    1. The cleaned notes are turned into numbers with TF-IDF. Each word gets a
       score that is high when the word appears in this note but is rare in
       the other notes.
    2. Two models learn from 80% of the data: Multinomial Naive Bayes and
       Logistic Regression.
    3. Both are tested on the same unseen 20%, and the better one is used
       in the app.

Part 11 adds the confusion matrix and the error analysis. Run this file on its
own to see a demo.
n = number of notes,
v = number of different words (the vocabulary size), c = number of categories.
"""

import csv
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score, precision_score,
                             recall_score)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

from data_io import load_labelled_dataset
from plots import plot_confusion_matrix
from text_utils import clean_many, clean_text

# The seed makes the random split the same every time, so results can be repeated.
RANDOM_SEED = 42


def split_data(texts, labels, test_size=0.2, seed=RANDOM_SEED):
    """Split the data into a training part and a testing part.

    Uses a fixed seed so everyone gets the same split, and keeps the same
    share of each category in both parts.
    Input:  texts (list of str), labels (list of str), test_size (float), seed (int)
    Output: (train_texts, test_texts, train_labels, test_labels)
    Time:   O(n)
    """
    if len(texts) != len(labels):
        raise ValueError("texts and labels must have the same length")
    # stratify=labels keeps the same share of each category in both parts,
    # so a small category such as Other is not missing from the test set.
    return train_test_split(texts, labels, test_size=test_size,
                            random_state=seed, stratify=labels)


def make_vectorizer():
    """Return a new, unfitted TF-IDF vectorizer with our settings."""
    # ngram_range=(1, 2) also uses pairs of words, such as "uni fee",
    # which carry more meaning than either word alone.
    # sublinear_tf uses 1 + log(count) instead of the raw count, so a word
    # repeated in one note does not get too much weight.
    return TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)


def build_features(train_texts, test_texts):
    """Learn the TF-IDF vocabulary from the training notes only, then turn
    both parts into number tables (matrices).

    Input:  train_texts, test_texts (lists of cleaned str)
    Output: (vectorizer, X_train, X_test)
    Time:   O(total number of words)
    """
    vectorizer = make_vectorizer()
    # fit_transform learns the vocabulary and the idf values from the training
    # notes only. The test notes are only transformed, so no information from
    # the test set leaks into training.
    X_train = vectorizer.fit_transform(train_texts)
    X_test = vectorizer.transform(test_texts)
    return vectorizer, X_train, X_test


class ExpenseClassifier:
    """A TF-IDF vectorizer plus one model, "nb" (Naive Bayes) or "lr" (Logistic Regression)."""

    MODEL_NAMES = {"nb": "Multinomial Naive Bayes", "lr": "Logistic Regression"}

    def __init__(self, model_name="nb"):
        """Create an untrained classifier. Time: O(1)"""
        if model_name not in self.MODEL_NAMES:
            raise ValueError("model_name must be 'nb' or 'lr'")
        self.model_name = model_name
        self.vectorizer = None
        if model_name == "nb":
            # alpha is the smoothing: every word gets a small extra count, so a
            # word never seen with a category does not make its chance zero.
            self.model = MultinomialNB(alpha=0.5)
        else:
            # liblinear is a solver that works well on small text datasets.
            # It trains one yes/no model per category ("one vs rest").
            self.model = LogisticRegression(solver="liblinear", max_iter=1000)

    def full_name(self):
        """Return the readable model name, for example "Logistic Regression"."""
        return self.MODEL_NAMES[self.model_name]

    def train(self, texts, labels):
        """Clean the notes, build TF-IDF features and fit the model.

        Time: O(n * v) for Naive Bayes, more for Logistic Regression
        because it repeats over the data several times.
        """
        cleaned = clean_many(texts)
        self.vectorizer = make_vectorizer()
        X_train = self.vectorizer.fit_transform(cleaned)
        self.model.fit(X_train, labels)

    def predict(self, text):
        """Return the predicted category for one raw note. Time: O(L + v * c)"""
        if self.vectorizer is None:
            raise RuntimeError("Train the classifier before predicting.")
        cleaned = clean_text(text)
        if cleaned == "":
            # Nothing useful is left after cleaning, so we cannot guess.
            return "Other"
        features = self.vectorizer.transform([cleaned])
        return self.model.predict(features)[0]

    def predict_many(self, texts):
        """Return the predicted category for each raw note in a list."""
        if self.vectorizer is None:
            raise RuntimeError("Train the classifier before predicting.")
        features = self.vectorizer.transform(clean_many(texts))
        return list(self.model.predict(features))

    def evaluate(self, texts, labels):
        """Return a dict with accuracy, precision, recall and f1 on the given data.

        Precision, recall and f1 are "macro" averages: worked out for each
        category, then averaged, so every category counts the same.
        Time: O(n * v * c)
        """
        predicted = self.predict_many(texts)
        return {
            "accuracy": accuracy_score(labels, predicted),
            "precision": precision_score(labels, predicted, average="macro", zero_division=0),
            "recall": recall_score(labels, predicted, average="macro", zero_division=0),
            "f1": f1_score(labels, predicted, average="macro", zero_division=0),
        }


def compare_models(texts, labels):
    """Train both models on the same split and compare them.

    Input:  texts, labels (lists of str)
    Output: (results, best) where results is a dict
            {"nb": metrics dict, "lr": metrics dict} and best is the trained
            ExpenseClassifier with the higher F1 score
    """
    # Split the raw notes once, so both models get exactly the same
    # training and testing notes. That makes the comparison fair.
    train_texts, test_texts, train_labels, test_labels = split_data(texts, labels)
    results = {}
    trained = {}
    for name in ("nb", "lr"):
        classifier = ExpenseClassifier(name)
        classifier.train(train_texts, train_labels)
        results[name] = classifier.evaluate(test_texts, test_labels)
        trained[name] = classifier
    best_name = max(results, key=lambda name: results[name]["f1"])
    return results, trained[best_name]


def save_correction(text, category, path):
    """Save a user's correction (text, right category) so it is used next time we train.

    Input:  text (str), category (str), path (str)
    Output: None
    Time:   O(1)
    """
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if new_file:
            writer.writerow(["description", "category"])
        writer.writerow([text, category])


def load_training_data(dataset_path, corrections_path):
    """Return (texts, labels) from the dataset plus any saved corrections."""
    texts, labels = load_labelled_dataset(dataset_path)
    if os.path.exists(corrections_path):
        more_texts, more_labels = load_labelled_dataset(corrections_path)
        texts = texts + more_texts
        labels = labels + more_labels
    return texts, labels


def error_analysis(classifier, texts, labels, path):
    """Write every wrong prediction (note, true category, predicted category) to a file
    and return the confusion matrix.

    The confusion matrix is a c x c table. Row i is the true category and
    column j the predicted one, so the numbers on the diagonal are correct
    answers and every other number is a mistake.

    Input:  classifier (trained ExpenseClassifier), texts and labels (lists of str),
            path (str) of the CSV file for the wrong predictions
    Output: (matrix, category_names). Time: O(n * v * c)
    """
    predicted = classifier.predict_many(texts)
    # sorted(set(...)) gives each category once, in a fixed order, so the rows
    # and columns of the matrix always mean the same thing.
    category_names = sorted(set(labels) | set(predicted))
    matrix = confusion_matrix(labels, predicted, labels=category_names)

    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["description", "true_category", "predicted_category"])
        for text, true_label, guess in zip(texts, labels, predicted):
            if true_label != guess:
                writer.writerow([text, true_label, guess])
    return matrix, category_names


def most_confused_pairs(matrix, category_names, count=3):
    """Return the most common mistakes as (true, predicted, times), biggest first.

    Only cells off the diagonal are mistakes. Time: O(c * c log c)
    """
    mistakes = []
    for i in range(len(category_names)):
        for j in range(len(category_names)):
            if i != j and matrix[i][j] > 0:
                mistakes.append((category_names[i], category_names[j], int(matrix[i][j])))
    mistakes.sort(key=lambda item: item[2], reverse=True)
    return mistakes[:count]


if __name__ == "__main__":
    # Demo: run this file on its own to train both models and compare them.
    project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(project_folder, "data", "raw", "expenses_labelled.csv")
    corrections_path = os.path.join(project_folder, "data", "processed", "corrections.csv")
    hard_path = os.path.join(project_folder, "data", "raw", "expenses_hard_test.csv")

    print("Demo of classifier.py: train and compare two models")
    print()
    texts, labels = load_training_data(dataset_path, corrections_path)
    train_texts, test_texts, train_labels, test_labels = split_data(clean_many(texts), labels)
    vectorizer, X_train, X_test = build_features(train_texts, test_texts)
    print("Notes:", len(texts), " Training:", len(train_texts), " Testing:", len(test_texts))
    print("TF-IDF features (words and word pairs):", len(vectorizer.vocabulary_))
    print()

    results, best = compare_models(texts, labels)
    print("Results on the 20% test notes (never seen in training)")
    print("Model".ljust(26) + "Accuracy  Precision  Recall    F1")
    for name, metrics in results.items():
        print(ExpenseClassifier.MODEL_NAMES[name].ljust(26)
              + format(metrics["accuracy"], ".3f").ljust(10)
              + format(metrics["precision"], ".3f").ljust(11)
              + format(metrics["recall"], ".3f").ljust(10)
              + format(metrics["f1"], ".3f"))
    print()
    print("Best model (higher F1):", best.full_name())
    print()

    # The 20% test notes come from the same templates as the training notes,
    # so the score above is very high. This second test uses 80 notes we wrote
    # by hand with new shops and new wording, to show the real limits.
    hard_texts, hard_labels = load_labelled_dataset(hard_path)
    hard = best.evaluate(hard_texts, hard_labels)
    print("Same model on", len(hard_texts), "hand-written notes with new wording:")
    print("  accuracy", format(hard["accuracy"], ".3f"), " f1", format(hard["f1"], ".3f"))
    print()

    print("Predictions for new notes")
    for note in ["Rs 850 foodpanda biryani", "careem to uni", "K Electric bill",
                 "panadol from dvago", "cinepax tickets", "semester fee"]:
        print(" ", note.ljust(28), "->", best.predict(note))
    print()

    # Part 11: where does the model go wrong? We use the hard notes, because
    # on the template test notes there are almost no mistakes to look at.
    wrong_path = os.path.join(project_folder, "outputs", "results", "wrong_predictions.csv")
    figure_path = os.path.join(project_folder, "outputs", "figures", "confusion_matrix.png")
    matrix, names = error_analysis(best, hard_texts, hard_labels, wrong_path)
    plot_confusion_matrix(matrix, names, figure_path)
    print("Error analysis on the hand-written notes")
    print("  wrong predictions saved to", os.path.relpath(wrong_path, project_folder))
    print("  confusion matrix chart saved to", os.path.relpath(figure_path, project_folder))
    print("  most common mistakes (true -> predicted, times):")
    for true_label, guess, times in most_confused_pairs(matrix, names):
        print("   ", true_label, "->", guess + ",", times)