"""
data_io.py - reading and writing files (owner: Nehal)

This module is the only place that touches files on disk. Every other module
asks data_io to read or write for it, so file errors are handled in one place.

Records
    A transaction row is passed around as a tuple:
        (date, description, amount, currency, category, kind)
    for example ("2026-11-03", "foodpanda biryani", 850.0, "PKR", "Food", "expense").
    A tuple is used because a saved record should not be changed by mistake.

Agreed interface (filled in by Part 4). n = number of rows in the file.
"""


class InvalidTransactionError(Exception):
    """Raised when an amount, date or category is not valid.

    Used by data_io, models and main whenever input is malformed.
    """


def parse_amount(text):
    """Turn text such as "850" or "1,200.50" into a positive float.

    Input:  text (str or number)
    Output: float greater than 0
    Raises: InvalidTransactionError if it is empty, not a number, or not positive
    Time:   O(L) where L is the length of the text
    """
    raise NotImplementedError("Part 4")


def parse_date(text):
    """Check that text is a real date in the form YYYY-MM-DD.

    Input:  text (str)
    Output: the same date as a str "YYYY-MM-DD"
    Raises: InvalidTransactionError if the format or the date is wrong
    Time:   O(1)
    """
    raise NotImplementedError("Part 4")


def read_ledger_csv(path):
    """Read a ledger CSV file into a list of record tuples.

    Rows that are malformed are skipped and counted, not crashed on.
    Input:  path (str) to a CSV with columns date,description,amount,currency,category,kind
    Output: (records, skipped) where records is a list of tuples and skipped is an int
    Raises: FileNotFoundError if the file does not exist
    Time:   O(n)
    """
    raise NotImplementedError("Part 4")


def write_ledger_csv(path, records):
    """Write a list of record tuples to a CSV file with a header row.

    Input:  path (str), records (list of tuples)
    Output: None
    Time:   O(n)
    """
    raise NotImplementedError("Part 4")


def load_labelled_dataset(path):
    """Read the labelled training data (description,category).

    Input:  path (str)
    Output: (texts, labels), two lists of the same length
    Raises: FileNotFoundError if the file does not exist
    Time:   O(n)
    """
    raise NotImplementedError("Part 4")


def read_json(path, default=None):
    """Read a JSON file. If the file is missing or broken, return default.

    Input:  path (str), default (any value to return on failure)
    Output: the dict or list stored in the file, or default
    Time:   O(size of file)
    """
    raise NotImplementedError("Part 4")


def write_json(path, data):
    """Save a dict or list to a JSON file.

    Input:  path (str), data (dict or list)
    Output: None
    Time:   O(size of data)
    """
    raise NotImplementedError("Part 4")


def append_text_lines(path, lines):
    """Add lines to the end of a text file (used for the cleaning log).

    Input:  path (str), lines (list of str)
    Output: None
    Time:   O(number of lines)
    """
    raise NotImplementedError("Part 4")
