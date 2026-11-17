"""
data_io.py - reading and writing files (owner: Nehal)

This module is the only place that touches files on disk. Every other module
asks data_io to read or write for it, so file errors are handled in one place.

Records
    A transaction row is passed around as a tuple:
        (date, description, amount, currency, category, kind)
    for example ("2026-11-03", "foodpanda biryani", 850.0, "PKR", "Food", "expense").
    A tuple is used because a saved record should not be changed by mistake.

n = number of rows in the file.
"""

import csv
import json
import os
from datetime import datetime

LEDGER_HEADER = ["date", "description", "amount", "currency", "category", "kind"]


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
    cleaned = str(text).strip().replace(",", "")
    if cleaned == "":
        raise InvalidTransactionError("Amount is empty.")
    try:
        amount = float(cleaned)
    except ValueError:
        raise InvalidTransactionError("Amount is not a number: " + str(text))
    # float() accepts "nan" and "inf", which are not real amounts.
    if amount != amount or amount in (float("inf"), float("-inf")):
        raise InvalidTransactionError("Amount is not a real number: " + str(text))
    if amount <= 0:
        raise InvalidTransactionError("Amount must be more than 0.")
    return amount


def parse_date(text):
    """Check that text is a real date in the form YYYY-MM-DD.

    Input:  text (str)
    Output: the same date as a str "YYYY-MM-DD"
    Raises: InvalidTransactionError if the format or the date is wrong
    Time:   O(1)
    """
    cleaned = str(text).strip()
    try:
        # strptime also rejects dates that do not exist, such as 2026-02-30.
        date = datetime.strptime(cleaned, "%Y-%m-%d")
    except ValueError:
        raise InvalidTransactionError("Date must look like 2026-11-03, got: " + cleaned)
    return date.strftime("%Y-%m-%d")


def read_ledger_csv(path):
    """Read a ledger CSV file into a list of record tuples.

    Rows that are malformed are skipped and counted, not crashed on.
    Input:  path (str) to a CSV with columns date,description,amount,currency,category,kind
    Output: (records, skipped) where records is a list of tuples and skipped is an int
    Raises: FileNotFoundError if the file does not exist
    Time:   O(n)
    """
    records = []
    skipped = 0
    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                date = parse_date(row["date"])
                amount = parse_amount(row["amount"])
                category = row["category"].strip()
                if category == "":
                    raise InvalidTransactionError("Category is empty.")
            except (InvalidTransactionError, KeyError, AttributeError):
                # KeyError: a column is missing. AttributeError: a short row gives None.
                skipped += 1
                continue
            description = (row.get("description") or "").strip()
            currency = (row.get("currency") or "PKR").strip().upper()
            kind = (row.get("kind") or "expense").strip().lower()
            records.append((date, description, amount, currency, category, kind))
    return records, skipped


def write_ledger_csv(path, records):
    """Write a list of record tuples to a CSV file with a header row.

    Input:  path (str), records (list of tuples)
    Output: None
    Time:   O(n)
    """
    _make_folder_for(path)
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(LEDGER_HEADER)
        writer.writerows(records)


def load_labelled_dataset(path):
    """Read the labelled training data (description,category).

    Rows with an empty description or category are skipped.
    Input:  path (str)
    Output: (texts, labels), two lists of the same length
    Raises: FileNotFoundError if the file does not exist
    Time:   O(n)
    """
    texts = []
    labels = []
    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            text = (row.get("description") or "").strip()
            label = (row.get("category") or "").strip()
            if text and label:
                texts.append(text)
                labels.append(label)
    return texts, labels


def read_json(path, default=None):
    """Read a JSON file. If the file is missing or broken, return default.

    Input:  path (str), default (any value to return on failure)
    Output: the dict or list stored in the file, or default
    Time:   O(size of file)
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default


def write_json(path, data):
    """Save a dict or list to a JSON file.

    Input:  path (str), data (dict or list)
    Output: None
    Time:   O(size of data)
    """
    _make_folder_for(path)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def append_text_lines(path, lines):
    """Add lines to the end of a text file (used for the cleaning log).

    Input:  path (str), lines (list of str)
    Output: None
    Time:   O(number of lines)
    """
    _make_folder_for(path)
    with open(path, "a", encoding="utf-8") as file:
        for line in lines:
            file.write(line + "\n")


def _make_folder_for(path):
    """Create the folder that will hold path, if it does not exist yet."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
