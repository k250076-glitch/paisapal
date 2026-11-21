"""
api_client.py - converting foreign money to PKR (owner: Nehal)

The app asks a free exchange-rate website (no API key) how many rupees one
unit of a currency is worth. The answer is saved to
data/processed/rates_cache.json, so the app still works without internet,
using the last saved rates.

Where the rates come from, in order:
    1. "live"      the website, if the internet works
    2. "cache"     the last rates we saved to rates_cache.json
    3. "fallback"  approximate rates written below, only if both fail

Data structures
    SUPPORTED_CURRENCIES  a set, so checking "do we support AED?" is O(1).
    the cache             a dict {currency: rupees per 1 unit}, plus the date
                          it was saved.

This is the first part to drop if the group falls behind.

c = number of currencies. Run this file on its own to see a demo.
"""

import os
from datetime import date

import requests

from data_io import InvalidTransactionError, parse_amount, read_json, write_json

# Free service, no API key needed. It returns how much of each currency
# 1 PKR buys, for example {"USD": 0.0036}.
RATES_URL = "https://open.er-api.com/v6/latest/PKR"

SUPPORTED_CURRENCIES = {"USD", "GBP", "EUR", "AED", "SAR", "CAD", "AUD", "CNY"}

PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(PROJECT_FOLDER, "data", "processed", "rates_cache.json")

# Approximate rupees per unit, used only when there is no internet and no
# cache yet. They are rough values and the app says so when it uses them.
FALLBACK_RATES = {"USD": 280.0, "GBP": 355.0, "EUR": 300.0, "AED": 76.0,
                  "SAR": 75.0, "CAD": 200.0, "AUD": 183.0, "CNY": 39.0}


def fetch_rates():
    """Ask the website for today's rates.

    Output: dict {currency: rupees per 1 unit}
    Raises: ConnectionError if there is no internet or the reply is not OK
    Time:   O(c) after the network call, c = number of currencies
    """
    try:
        # timeout stops the app from waiting forever on a slow connection.
        reply = requests.get(RATES_URL, timeout=5)
    except requests.exceptions.RequestException as error:
        raise ConnectionError("Could not reach the rates website: " + str(error))
    if reply.status_code != 200:
        raise ConnectionError("Rates website answered with status " + str(reply.status_code))
    try:
        data = reply.json()
    except ValueError:
        raise ConnectionError("Rates website did not send valid JSON.")
    if data.get("result") != "success" or "rates" not in data:
        raise ConnectionError("Rates website sent an unexpected reply.")

    rates = {}
    for currency in SUPPORTED_CURRENCIES:
        per_rupee = data["rates"].get(currency)
        # The website says how much USD 1 PKR buys. We want the opposite:
        # how many PKR 1 USD buys, so we take 1 divided by the value.
        if per_rupee:
            rates[currency] = round(1 / per_rupee, 4)
    return rates


def get_rates(cache_path=CACHE_PATH):
    """Return rates from the website, or from the cache if the website fails.

    Output: (rates dict, source) where source is "live", "cache" or "fallback"
    Time:   O(c)
    """
    try:
        rates = fetch_rates()
        write_json(cache_path, {"saved_on": date.today().isoformat(), "rates": rates})
        return rates, "live"
    except ConnectionError:
        pass
    cached = read_json(cache_path, default=None)
    if isinstance(cached, dict) and cached.get("rates"):
        return cached["rates"], "cache"
    return dict(FALLBACK_RATES), "fallback"


def convert_to_pkr(amount, currency, cache_path=CACHE_PATH):
    """Convert an amount in a foreign currency to PKR.

    Input:  amount (float or str), currency (str such as "USD")
    Output: (amount in PKR rounded to 2 places, source "live", "cache" or "fallback")
    Raises: InvalidTransactionError for a bad amount or an unsupported currency
    Time:   O(c)
    """
    amount = parse_amount(amount)
    currency = str(currency).strip().upper()
    if currency == "PKR":
        return round(amount, 2), "none needed"
    if currency not in SUPPORTED_CURRENCIES:
        raise InvalidTransactionError("Currency not supported: " + currency)
    rates, source = get_rates(cache_path)
    if currency not in rates:
        raise InvalidTransactionError("No rate available for " + currency)
    return round(amount * rates[currency], 2), source


if __name__ == "__main__":
    # Demo: run this file on its own to convert a few amounts.
    print("Demo of api_client.py: converting to PKR")
    print()
    rates, source = get_rates()
    print("Rates source:", source)
    if source == "fallback":
        print("(no internet and no saved rates yet, so approximate rates are used)")
    for currency in sorted(rates):
        print(" ", currency, "1 =", "Rs", format(rates[currency], ",.2f"))
    print()
    for amount, currency in [(20, "USD"), (150, "AED"), (500, "PKR")]:
        pkr, used = convert_to_pkr(amount, currency)
        print(" ", amount, currency, "->", "Rs", format(pkr, ",.2f"))
    print()
    print("An unsupported currency is rejected:")
    try:
        convert_to_pkr(10, "XYZ")
    except InvalidTransactionError as error:
        print("  InvalidTransactionError:", error)
