"""
api_client.py - converting foreign money to PKR (owner: Nehal)

The app asks a free exchange-rate website (no API key) how many rupees one
unit of a currency is worth. The answer is saved to
data/processed/rates_cache.json, so the app still works without internet,
using the last saved rates.

Data structures
    SUPPORTED_CURRENCIES  a set, so checking "do we support AED?" is O(1).
    the cache             a dict {currency: rupees per 1 unit}, plus the date
                          it was saved.

This is the first part to drop if the group falls behind.

Agreed interface (filled in by Part 10).
"""

# Filled in by Part 10.
SUPPORTED_CURRENCIES = set()


def fetch_rates():
    """Ask the website for today's rates.

    Output: dict {currency: rupees per 1 unit}
    Raises: ConnectionError if there is no internet or the reply is not OK
    Time:   O(c) after the network call, c = number of currencies
    """
    raise NotImplementedError("Part 10")


def get_rates():
    """Return rates from the website, or from the cache if the website fails.

    Output: (rates dict, source) where source is "live" or "cache"
    Raises: ConnectionError if both the website and the cache fail
    Time:   O(c)
    """
    raise NotImplementedError("Part 10")


def convert_to_pkr(amount, currency):
    """Convert an amount in a foreign currency to PKR.

    Input:  amount (float), currency (str such as "USD")
    Output: (amount in PKR rounded to 2 places, source "live" or "cache")
    Raises: InvalidTransactionError for an unsupported currency
    Time:   O(c)
    """
    raise NotImplementedError("Part 10")
