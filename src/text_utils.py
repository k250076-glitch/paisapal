"""
text_utils.py - cleaning messy expense text (owner: Zain)

Expense notes are messy, for example "Rs 850 FOODPANDA biryani!!" or
"food panda biriyani". Before the classifier can learn from them we turn
every note into a clean, simple form, for example "foodpanda biryani".

Data structures
    STOP_WORDS     a set, because we check "is this word a stop-word?" for every
                   word, and checking a set takes O(1) time.
    PHRASE_MAP     a dict from a two-word name to one joined word,
                   for example "food panda" -> "foodpanda".
    NORMALISE_MAP  a dict from a spelling variant to one standard word,
                   for example "fp" -> "foodpanda". Looking up a key is O(1).

L = number of characters in a note, N = total characters in all notes.
"""

import re

from data_io import append_text_lines

# Words that appear in notes of every category, so they do not help the
# classifier decide. Includes English and Roman Urdu filler words, money
# words and payment apps (paying by JazzCash says nothing about the category).
STOP_WORDS = {
    "a", "an", "the", "to", "from", "for", "with", "at", "on", "in", "of",
    "and", "by", "via", "my", "new", "paid", "bought", "order", "back",
    "rs", "pkr", "rupees", "cash", "card", "urgent",
    "jazzcash", "easypaisa", "sadapay", "nayapay",
    "ka", "ki", "ke", "ko", "se", "pe", "liya", "lia", "li", "kiya", "diye",
    "karwaya", "karwaye", "bhai", "wala", "wali",
}

# Names that people write as two words. They are joined first, so that the
# rest of the cleaning sees one word.
PHRASE_MAP = {
    "food panda": "foodpanda",
    "in drive": "indrive",
    "k electric": "kelectric",
    "sui gas": "suigas",
    "storm fiber": "stormfiber",
    "pizza hut": "pizzahut",
    "green line": "greenline",
    "total parco": "totalparco",
    "mobile load": "mobileload",
}

# Short forms and common misspellings mapped to one standard word.
NORMALISE_MAP = {
    "fp": "foodpanda",
    "mcd": "mcdonalds",
    "biriyani": "biryani",
    "biryni": "biryani",
    "bryani": "biryani",
    "kareem": "careem",
    "ubr": "uber",
    "petrl": "petrol",
    "patrol": "petrol",
    "chingchi": "qingqi",
    "electrc": "electric",
    "easyload": "mobileload",
    "medicin": "medicine",
    "medcine": "medicine",
    "dawai": "medicine",
    "grocries": "groceries",
    "grocery": "groceries",
    "tikets": "tickets",
    "ticket": "tickets",
    "smester": "semester",
}

# Anything that is not a lowercase letter or a space becomes a space.
# This removes digits, symbols and punctuation in one step.
NOT_LETTER = re.compile(r"[^a-z ]+")


def clean_text(text):
    """Clean one expense note.

    Steps: lowercase, join multi-word names ("food panda" -> "foodpanda"),
    remove digits and symbols, map variants with NORMALISE_MAP, drop stop-words.
    Input:  text (str)
    Output: cleaned str, may be "" if nothing useful is left
    Time:   O(L)
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = NOT_LETTER.sub(" ", text)
    # Squeeze many spaces into one so the phrase matching below works.
    text = " ".join(text.split())
    # Adding a space at both ends means " in drive " only matches the whole
    # words, not the end of a longer word such as "within drive".
    text = " " + text + " "
    for phrase, joined in PHRASE_MAP.items():
        # A loop, because one replace() pass can miss a phrase that comes
        # straight after another copy of itself.
        while " " + phrase + " " in text:
            text = text.replace(" " + phrase + " ", " " + joined + " ")

    words = []
    for word in text.split():
        # get() returns the standard word, or the word itself if it is not in the map.
        word = NORMALISE_MAP.get(word, word)
        if word in STOP_WORDS or len(word) < 2:
            continue
        words.append(word)
    return " ".join(words)


def clean_many(texts):
    """Clean a list of notes with a list comprehension.

    Input:  texts (list of str)
    Output: list of cleaned str, same length and order
    Time:   O(N)
    """
    return [clean_text(text) for text in texts]


def log_cleaning(originals, cleaned, path):
    """Write "original -> cleaned" lines to a text log so we can check the cleaning.

    Input:  originals (list of str), cleaned (list of str), path (str)
    Output: None
    Time:   O(number of notes)
    """
    lines = [original + " -> " + result for original, result in zip(originals, cleaned)]
    append_text_lines(path, lines)


if __name__ == "__main__":
    # Demo: run this file on its own to see the cleaning on real notes.
    import os
    from data_io import load_labelled_dataset

    project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(project_folder, "data", "raw", "expenses_labelled.csv")

    print("Demo of text_utils.py: messy note -> cleaned note")
    print()
    texts, labels = load_labelled_dataset(dataset_path)
    for text, label in zip(texts[:10], labels[:10]):
        print(" ", text.ljust(40), "->", clean_text(text).ljust(28), "(" + label + ")")
    print()

    examples = ["Rs 850 FOODPANDA biryani!!", "food panda biriyani via jazzcash",
                "fp deal", "K Electric bill paid", ""]
    print("Hand-picked examples, including an empty note")
    for text in examples:
        print(" ", repr(text).ljust(40), "->", repr(clean_text(text)))