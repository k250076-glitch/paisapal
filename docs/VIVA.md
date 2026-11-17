# PaisaPal viva practice

Likely viva and exam questions with short answers. New questions are added
with each part. Each member should be able to answer every question about
their own module, and the general questions.

## General (everyone)

**Q: What does PaisaPal do?**
A: It is a Python console app that takes messy expense notes in English or
Roman Urdu, cleans them, predicts their category with a trained classifier,
tracks monthly budgets, converts foreign currency to PKR and draws charts.

**Q: How did you divide the work?**
A: Polani built the classes, the ledger, the budget and the menu. Zain built
text cleaning, TF-IDF and the two classifiers. Nehal built file reading and
writing, the currency API, the NumPy and Pandas analysis and the charts. Each
of us committed our own parts from our own GitHub account.

**Q: Why did you write the interfaces before the code?**
A: So that everyone knew the exact function names, inputs and outputs of the
other modules. We could build our parts at the same time and they fitted
together at the end without rewriting.

**Q: What is in .gitignore and why?**
A: Python cache files, virtual environments, files the program creates while
running (in data/processed and outputs) and any .env file. They are either
generated again on every run or could contain private data.

**Q: Why pin versions in requirements.txt?**
A: So the program runs the same way on every computer. A newer library version
could change a function and break our code.

**Q: Where does the data come from, and is there personal data in it?**
A: The labelled dataset is a starter set of expense notes built from templates
of real-style notes. It has no names, phone numbers or account details.

## Polani: Transaction classes (Part 2)

**Q: What is an abstract base class, and why is Transaction one?**
A: A class that cannot be created on its own because some methods have no
body and must be written by the child classes. A plain "transaction" is not
real: it is always an expense or an income, so Transaction is abstract and
`signed_amount()` and `kind()` are abstract methods.

**Q: What happens if you try `Transaction("2026-11-03", "x", 5, "Food")`?**
A: Python raises a TypeError, because you cannot create an object of a class
that still has abstract methods.

**Q: Show polymorphism in your code.**
A: Both child classes have `signed_amount()`, but an expense returns
`-amount` and an income returns `+amount`. The balance is the sum of
`t.signed_amount()` over a mixed list, and Python calls the right version for
each object without any if statement.

**Q: Where is encapsulation?**
A: The amount is stored as `self.__amount`, which outside code cannot reach.
It can only be changed through the `amount` setter, which checks it is a
positive number and raises InvalidTransactionError otherwise.

**Q: What is the difference between overriding and overloading?**
A: Overriding is a child class writing its own version of a parent method,
like `describe()` here. Python has no overloading in the Java sense (two
methods with the same name and different parameters); default arguments are
used instead.

**Q: What does `super().__init__(...)` do?**
A: It runs the parent class's constructor, so the child does not repeat the
code that stores the date, description and amount.

**Q: Why is CATEGORIES a tuple?**
A: The categories are fixed. A tuple cannot be changed, so no code can add or
remove a category by mistake.

## Zain: text cleaning (Part 3)

**Q: Why do you clean the text before training?**
A: "FOODPANDA", "food panda" and "fp" all mean the same thing. Without
cleaning, the classifier would treat them as three different words and learn
less from each one.

**Q: Why is STOP_WORDS a set and not a list?**
A: We check every word against it. A set uses hashing and answers "is this
word inside?" in O(1) time on average. A list would check items one by one,
which is O(s) for s stop-words.

**Q: Why are JazzCash and Easypaisa stop-words?**
A: They appear in notes of every category. Paying by JazzCash says nothing
about whether it was food or transport, so they would only add noise.

**Q: Why do you remove digits?**
A: The amount in the note ("rs 850") does not tell us the category, and
every different number would become a separate useless feature.

**Q: What is the time complexity of cleaning one note?**
A: O(L) for a note of L characters: lowercasing, the regular expression and
splitting all go through the text a fixed number of times, and each word
lookup in the set and dicts is O(1).

**Q: What are the limits of your cleaning?**
A: Roman Urdu has many spellings, and our map only covers the ones we saw.
A new spelling such as "biryanee" stays as it is, and the classifier may not
recognise it.

## Nehal: file input and output (Part 4)

**Q: Why is a record a tuple?**
A: A saved record should not change by accident. A tuple cannot be changed
after it is made, and it is also slightly smaller and faster than a list.

**Q: What happens if the ledger CSV has a bad row?**
A: `read_ledger_csv()` skips it, counts it and keeps reading. The sample file
has 4 bad rows on purpose (empty amount, "abc" as amount, empty category,
empty date) and the function returns 270 good records and skipped = 4.

**Q: Why did you write a custom exception?**
A: `InvalidTransactionError` tells the caller exactly what went wrong (a bad
amount, date or category) instead of a general ValueError, so the menu can
catch it and show a clear message.

**Q: Why not use a bare `except:`?**
A: It would also catch real bugs and even Ctrl+C, and hide them. We catch only
the errors we expect, such as FileNotFoundError and JSONDecodeError.

**Q: What does `read_json()` do if the file does not exist?**
A: It returns the default value instead of crashing. That is how the app
starts the first time, before any budget or rate cache has been saved.

**Q: Why does `parse_amount()` check for "nan" and "inf"?**
A: Python's `float()` accepts them, but they are not real amounts and would
break every total.
