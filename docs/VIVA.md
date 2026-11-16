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
