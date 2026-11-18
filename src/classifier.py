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

Parts 8 and 11 fill in the models and the error analysis. n = number of notes,
v = number of different words (the vocabulary size), c = number of categories.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

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


def build_features(train_texts, test_texts):
    """Learn the TF-IDF vocabulary from the training notes only, then turn
    both parts into number tables (matrices).

    Input:  train_texts, test_texts (lists of cleaned str)
    Output: (vectorizer, X_train, X_test)
    Time:   O(total number of words)
    """
    # ngram_range=(1, 2) also uses pairs of words, such as "uni fee",
    # which carry more meaning than either word alone.
    # sublinear_tf uses 1 + log(count) instead of the raw count, so a word
    # repeated in one note does not get too much weight.
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
    # fit_transform learns the vocabulary and the idf values from the training
    # notes only. The test notes are only transformed, so no information from
    # the test set leaks into training.
    X_train = vectorizer.fit_transform(train_texts)
    X_test = vectorizer.transform(test_texts)
    return vectorizer, X_train, X_test


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


if __name__ == "__main__":
    # Demo: run this file on its own to see the split and the TF-IDF features.
    import os
    from data_io import load_labelled_dataset
    from text_utils import clean_many

    project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(project_folder, "data", "raw", "expenses_labelled.csv")

    print("Demo of classifier.py: split and TF-IDF")
    print()
    texts, labels = load_labelled_dataset(dataset_path)
    cleaned = clean_many(texts)
    train_texts, test_texts, train_labels, test_labels = split_data(cleaned, labels)
    print("Notes in the dataset:", len(texts))
    print("Training notes:", len(train_texts), " Testing notes:", len(test_texts))
    print()

    vectorizer, X_train, X_test = build_features(train_texts, test_texts)
    print("Vocabulary size (different words and word pairs):", len(vectorizer.vocabulary_))
    print("Training matrix shape:", X_train.shape, "(notes x features)")
    print()

    example = "foodpanda biryani"
    row = vectorizer.transform([example])
    names = vectorizer.get_feature_names_out()
    print("TF-IDF scores for the note:", example)
    for index in row.nonzero()[1]:
        print(" ", names[index].ljust(20), round(row[0, index], 3))