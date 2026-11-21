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

**Q: What does `if __name__ == "__main__":` at the bottom of each file do?**
A: The code under it runs only when that file is run directly, for example
with the Run button. When another file imports it, `__name__` is the module
name instead, so the demo is skipped.

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

## Polani: Ledger and Budget (Part 5)

**Q: Why is the ledger a list?**
A: Transactions come one after another and we keep their order. Adding to the
end of a list is O(1) on average, and most reports have to look at every
transaction anyway, which is O(n) whatever we use.

**Q: Why is the budget a dict?**
A: We always ask "what is the limit for Food?". A dict finds a key in O(1)
using hashing, while a list of pairs would have to search, O(k).

**Q: How does `balance()` use polymorphism?**
A: It adds up `t.signed_amount()` for every transaction. Expenses return a
negative amount and income a positive one, so there is no if statement.

**Q: What is the lambda in `largest_expenses()`?**
A: `key=lambda t: t.amount` is a small unnamed function that tells `sort()` to
compare transactions by their amount. Sorting is O(n log n).

**Q: When is a category "NEAR" its budget?**
A: When spending reaches 80% of the limit (`warn_at=0.8`) but is not over it.

**Q: Why does the demo load 257 transactions when data_io read 270 records?**
A: 13 records are in USD, AED or GBP. `from_records()` skips them until the
currency part (Part 10) converts them to PKR.

## Zain: train/test split and TF-IDF (Part 6)

**Q: Why split the data into training and testing sets?**
A: To measure the model honestly. It learns from 80% of the notes and is
tested on the 20% it has never seen. Testing on the training notes would
only show how well it memorised them.

**Q: What does `stratify=labels` do?**
A: It keeps the share of each category the same in both parts. Without it, a
small category such as Other could end up with very few test notes.

**Q: Why a fixed random seed?**
A: So the split is the same every time. Results can be repeated, and both
models are compared on exactly the same test notes.

**Q: Explain TF-IDF in simple words.**
A: Each word in a note gets a score. TF is how often it appears in that note;
IDF is high when few notes contain the word. Multiplying them gives a high
score to words that are frequent here but rare overall, like "foodpanda", and
a low score to words found everywhere.

**Q: Why fit the vectorizer on the training notes only?**
A: If it also learned from the test notes, information about the test set
would leak into training and the accuracy would look better than it is.

**Q: What is a sparse matrix and why is it used?**
A: The TF-IDF table has about 1,300 columns, but each note uses only a few.
A sparse matrix stores only the non-zero values, which saves a lot of memory.

**Q: Why use word pairs (bigrams)?**
A: A pair such as "uni fee" or "foodpanda biryani" carries more meaning than
each word alone and helps the model separate similar categories.

## Nehal: monthly spending matrix (Part 7)

**Q: What is the shape of the matrix and what does each cell mean?**
A: One row per month and one column per category, 6 x 8 for the sample data.
Each cell is the total spent in that category in that month.

**Q: What does `axis=0` mean in `matrix.sum(axis=0)`?**
A: Work down the rows, giving one answer per column, so one total per
category. `axis=1` works across the columns, giving one total per month.

**Q: What is broadcasting?**
A: When NumPy combines arrays of different shapes. The budget has 8 values and
the matrix is 6 x 8, so NumPy repeats the budget for each of the 6 months and
compares cell by cell, without a loop.

**Q: What is a boolean mask?**
A: An array of True/False the same shape as the matrix. `matrix > budget`
gives True where spending is over the limit. It can then pick out those cells.

**Q: Why NumPy instead of a list of lists?**
A: NumPy stores the numbers in one block and runs sums and comparisons in fast
compiled code, so whole-grid operations need no Python loops.

**Q: Why are the month and category positions kept in dicts?**
A: To find the row and column of a record in O(1). Searching a list for the
month and category every time would be O(m + k) per record.

## Zain: two classifiers and comparing them (Part 8)

**Q: How does Naive Bayes decide the category?**
A: For each category it multiplies the chance of the category by the chance
of each word in the note given that category, and picks the highest. "Naive"
means it treats the words as independent of each other.

**Q: What is alpha=0.5?**
A: Smoothing. Every word gets a small extra count, so a word never seen with a
category does not make that category's chance zero.

**Q: How is Logistic Regression different?**
A: It learns a weight for every word for every category and adds them up. It
trains one yes/no model per category (one vs rest) and picks the most likely.
It is slower to train because it goes over the data several times.

**Q: Why compare on the same split?**
A: So both models see exactly the same training and test notes. Otherwise one
could look better only because it got easier test notes.

**Q: What are precision, recall and F1?**
A: Precision: of the notes we called Food, how many really were Food. Recall:
of the real Food notes, how many we found. F1 combines the two. We use the
macro average so every category counts the same.

**Q: Why choose the best model by F1 instead of accuracy?**
A: Accuracy can look good while a small category is always wrong. Macro F1
drops when any category is handled badly.

**Q: Your accuracy is 99.7 percent. Is the model really that good?**
A: No. Our training notes come from templates, so the test notes are very
similar. On 80 hand-written notes with new wording it gets about 51 percent.
That is the honest score, and more varied real data would improve it.

**Q: What happens to user corrections?**
A: `save_correction()` adds the note and the right category to
corrections.csv. Next time we train, `load_training_data()` includes them.

## Nehal: Pandas summary and lambda helpers (Part 9)

**Q: What does errors="coerce" do?**
A: A value that cannot be turned into a number or date becomes missing (NaN
or NaT) instead of crashing. Then `dropna()` removes those rows.

**Q: What does groupby with agg do?**
A: It puts the rows into groups with the same month and category, then works
out the sum, count and mean of the amount for each group in one step.

**Q: What is a lambda and where did you use one?**
A: A small function with no name, written in one line. We used one as the
sort key in `top_spending_days()`, in `filter` for `large_expenses()` and in
`map` for `amounts_in_thousands()`.

**Q: Why fill a missing category with "Other" instead of dropping the row?**
A: The amount and date are still good, so the money still counts in the
totals. Only the label is missing.

## Nehal: currency conversion with a cache (Part 10)

**Q: Where do the rates come from?**
A: First the website. If that fails, the last rates saved in
rates_cache.json. If there is no cache yet, rough built-in rates.

**Q: Why the cache?**
A: So the app still works without internet, and does not depend on the
website being up during the demo.

**Q: Why a timeout?**
A: Without it, a slow connection could make the app wait forever.

**Q: The website gives USD per 1 PKR. How do you get PKR per 1 USD?**
A: 1 divided by that value. For example 1 / 0.0036 is about 277.78.

**Q: How did you test it without internet?**
A: With a fake (mocked) `requests.get` that returns a good reply, an error
status, bad JSON and no connection, and we checked the source each time.

**Q: Why is SUPPORTED_CURRENCIES a set?**
A: Checking if a currency is in a set is O(1) on average. We only need "is it
there", not an order.

## Zain: confusion matrix and error analysis (Part 11)

**Q: What is a confusion matrix?**
A: A table with one row per true category and one column per predicted
category. Each cell counts the notes. The diagonal is the correct answers;
everything else is a mistake, and the cell tells you which category was
confused with which.

**Q: What did the error analysis show?**
A: On the 80 hand-written notes most mistakes were predicted as Food, for
example 7 Other notes and 4 Bills notes. Food is the biggest and most varied
category, so for unknown words it is the model's safest guess.

**Q: Why run it on the hand-written notes and not the normal test set?**
A: The normal test notes come from the same templates as the training notes,
so there are almost no mistakes to study. The hand-written notes show the
real weaknesses.

**Q: How would you improve the model?**
A: More varied training notes, and the corrections users make in the menu.
They are saved to corrections.csv and added the next time the model trains.

**Q: Why sort the category names before building the matrix?**
A: So rows and columns are always in the same order and the chart labels
match the numbers.

## Nehal: spending charts (Part 12)

**Q: Which charts does the app draw?**
A: A bar chart of total spending per category, a line chart of total spending
per month and a grouped bar chart of spending next to the budget.

**Q: Where does the chart data come from?**
A: The NumPy matrix. `matrix.sum(axis=0)` gives the category totals and
`matrix.sum(axis=1)` gives the monthly totals.

**Q: How are the two bars in a group placed side by side?**
A: `np.arange` gives the group positions 0, 1, 2 and so on. The spent bar is
drawn half a bar width to the left and the budget bar half a width to the right.

**Q: Why call `plt.close()` after saving?**
A: Every open figure uses memory. Closing it frees the memory, so drawing many
charts does not slow the program down.

**Q: Why does the line chart start at 0?**
A: If the axis started at the smallest value, a small change would look huge.
Starting at 0 shows the real size of the change.

**Q: What is the "Agg" back end?**
A: It draws charts straight into image files without opening a window, so the
menu never stops and waits for a window to be closed.

## Polani: the menu (Part 13)

**Q: How does the menu work?**
A: A `while True` loop prints the options, reads a choice and calls one
function for it. Choice 9 saves and uses `break` to leave the loop.

**Q: What happens if the user types "abc" as an amount?**
A: `ask_amount()` catches the `InvalidTransactionError` from `parse_amount()`,
prints the reason and asks again. The program never crashes on bad input.

**Q: How does the user correct a wrong category?**
A: After the prediction the menu lists the categories. Enter keeps the guess;
a number picks another. A correction is saved to corrections.csv and used the
next time the model trains.

**Q: When is the data saved?**
A: After every change, to data/processed/ledger.csv and budget.json, so
nothing is lost if the window is closed.

**Q: Why are the foreign rows converted with one call to `get_rates()`?**
A: Each call may wait for the website. Asking once and using the same rates for
every row means at most one wait.

**Q: Which modules does main.py use?**
A: All of them: models for the classes, classifier for predictions, api_client
for currency, analysis for the matrix and Pandas, plots for charts and
data_io for files.

## Everyone: testing (Part 14)

**Q: How do you run the tests?**
A: From the project folder, `python -m unittest discover tests`, or open a
test file in VS Code and press Run. All 71 tests pass.

**Q: Why unittest and not pytest?**
A: unittest comes with Python, so nothing extra needs to be installed.

**Q: Which edge cases did you test?**
A: Empty input, one element, duplicates, large input, invalid input, a missing
file and no network. Each test file has examples of each.

**Q: How did you test the currency code without the internet?**
A: With `unittest.mock.patch`, which replaces `requests.get` with a fake
during the test. The fake returns a good reply, an error or raises a
connection error, and we check where the rates came from.

**Q: Why does each file test use a temporary folder?**
A: So the tests never change our real data files, and every test starts from
an empty folder. The folder is deleted afterwards in `tearDown()`.

**Q: What does `setUp()` do?**
A: It runs before every test in the class, to prepare the same starting point
each time.

## How to demo in the viva (everyone)

1. Open the project folder in VS Code.
2. Open `src/main.py` and press Run. Use the menu in this order: 5 (Food
   budget 12000), 1 (`foodpanda biryani`, 850, Enter, Enter), 1 again
   (`shoe polish wala`, 200, pick Other), 2 (`amazon book`, USD, 20), 6, 7,
   8, 9.
3. When asked about your own module, open your file and press Run to show its
   demo, then open its test file and press Run to show the tests pass.
4. If the instructor asks to see a chart, open `outputs/figures`.

If something goes wrong in the demo, stay calm and explain what the code
should do. Deleting the files in `data/processed` resets the app to the sample
data.

**Q: Can you show the app working without the internet?**
A: Yes. The currency option then uses the saved rates or the built-in ones and
prints where the rate came from. Everything else works offline.

**Q: What would you improve with more time?**
A: More real, varied training notes, because the model scores about 51 percent
on new wording. Also budgets that can change month by month.

