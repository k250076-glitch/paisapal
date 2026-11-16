"""
text_utils.py - cleaning messy expense text (owner: Zain)

Expense notes are messy, for example "Rs 850 FOODPANDA biryani!!" or
"food panda biriyani". Before the classifier can learn from them we turn
every note into a clean, simple form, for example "foodpanda biryani".

Data structures
    STOP_WORDS     a set, because we check "is this word a stop-word?" for every
                   word, and checking a set takes O(1) time.
    NORMALISE_MAP  a dict from a spelling variant to one standard word,
                   for example "fp" -> "foodpanda". Looking up a key is O(1).

Agreed interface (filled in by Part 3). L = number of characters in a note,
N = total characters in all notes.
"""

# Filled in by Part 3.
STOP_WORDS = set()
NORMALISE_MAP = {}


def clean_text(text):
    """Clean one expense note.

    Steps: lowercase, join multi-word names ("food panda" -> "foodpanda"),
    remove digits and symbols, drop stop-words, map variants with NORMALISE_MAP.
    Input:  text (str)
    Output: cleaned str, may be "" if nothing useful is left
    Time:   O(L)
    """
    raise NotImplementedError("Part 3")


def clean_many(texts):
    """Clean a list of notes with a list comprehension.

    Input:  texts (list of str)
    Output: list of cleaned str, same length and order
    Time:   O(N)
    """
    raise NotImplementedError("Part 3")


def log_cleaning(originals, cleaned, path):
    """Write "original -> cleaned" lines to a text log so we can check the cleaning.

    Input:  originals (list of str), cleaned (list of str), path (str)
    Output: None
    Time:   O(number of notes)
    """
    raise NotImplementedError("Part 3")
