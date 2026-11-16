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

Agreed interface (filled in by Parts 6, 8 and 11). n = number of notes,
v = number of different words (the vocabulary size), c = number of categories.
"""


def split_data(texts, labels, test_size=0.2, seed=42):
    """Split the data into a training part and a testing part.

    Uses a fixed seed so everyone gets the same split, and keeps the same
    share of each category in both parts.
    Input:  texts (list of str), labels (list of str), test_size (float), seed (int)
    Output: (train_texts, test_texts, train_labels, test_labels)
    Time:   O(n)
    """
    raise NotImplementedError("Part 6")


def build_features(train_texts, test_texts):
    """Learn the TF-IDF vocabulary from the training notes only, then turn
    both parts into number tables (matrices).

    Input:  train_texts, test_texts (lists of cleaned str)
    Output: (vectorizer, X_train, X_test)
    Time:   O(total number of words)
    """
    raise NotImplementedError("Part 6")


class ExpenseClassifier:
    """A TF-IDF vectorizer plus one model, "nb" (Naive Bayes) or "lr" (Logistic Regression)."""

    def __init__(self, model_name="nb"):
        """Create an untrained classifier. Time: O(1)"""
        raise NotImplementedError("Part 8")

    def train(self, texts, labels):
        """Clean the notes, build TF-IDF features and fit the model.

        Time: O(n * v) for Naive Bayes, more for Logistic Regression
        because it repeats over the data several times.
        """
        raise NotImplementedError("Part 8")

    def predict(self, text):
        """Return the predicted category for one raw note. Time: O(L + v * c)"""
        raise NotImplementedError("Part 8")

    def evaluate(self, texts, labels):
        """Return a dict with accuracy, precision, recall and f1 on the given data.

        Time: O(n * v * c)
        """
        raise NotImplementedError("Part 8")


def compare_models(texts, labels):
    """Train both models on the same split and compare them.

    Input:  texts, labels (lists of str)
    Output: (results, best) where results is a dict
            {"nb": metrics dict, "lr": metrics dict} and best is the trained
            ExpenseClassifier with the higher F1 score
    """
    raise NotImplementedError("Part 8")


def save_correction(text, category, path):
    """Save a user's correction (text, right category) so it is used next time we train.

    Input:  text (str), category (str), path (str)
    Output: None
    Time:   O(1)
    """
    raise NotImplementedError("Part 8")


def error_analysis(classifier, texts, labels, path):
    """Write every wrong prediction (note, true category, predicted category) to a file
    and return the confusion matrix.

    Output: (matrix, category_names). Time: O(n * v * c)
    """
    raise NotImplementedError("Part 11")
