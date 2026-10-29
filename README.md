[![Tests](https://github.com/Farscent/python-expense-tracker/actions/workflows/tests.yml/badge.svg)](https://github.com/Farscent/python-expense-tracker/actions/workflows/tests.yml)

# Python Expense Tracker

A small command-line program for recording expenses in a CSV file and summarizing them by category and month. It uses **only Python's standard library**.

**Project question:** How can a simple Python program store records reliably and turn them into a useful monthly summary?

## Learning objectives

- Organize logic into small functions.
- Use a dataclass to represent a record.
- Read and append CSV files with the csv module.
- Validate dates and user input.
- Use Decimal for exact decimal money calculations.
- Build a command-line interface with argparse.
- Test behavior using temporary files.

## Run the project

Install **Python 3.11, 3.12, or 3.13**, clone the project, and enter its folder:

~~~bash
git clone https://github.com/Farscent/python-expense-tracker.git
cd python-expense-tracker
python tracker.py --help
~~~

There are no packages to install. All examples use Indonesian rupiah (IDR); the program assumes one currency throughout.

First, inspect the fictional sample data:

~~~bash
python tracker.py --file data/sample_expenses.csv list
python tracker.py --file data/sample_expenses.csv summary --month 2025-03
~~~

The March sample contains five expenses totaling **IDR 143,000.00**:

| Category | March total (IDR) |
|---|---:|
| Education | 45,000.00 |
| Entertainment | 30,000.00 |
| Food | 43,000.00 |
| Transport | 25,000.00 |
| **Total** | **143,000.00** |

The April row is excluded by the March filter.

## Record your own expenses

~~~bash
python tracker.py add --date 2025-03-01 --category food --amount 18000 --note "Coffee"
python tracker.py add --date 2025-03-02 --category transport --amount 5000 --note "Bus"
python tracker.py list --month 2025-03
python tracker.py summary --month 2025-03
~~~

If omitted, the date defaults to today. A successful add appends a new record to <code>data/expenses.csv</code>. Repeating an add command records another expense; it does not update the previous one.

The <code>--file</code> option must appear **before** the command:

~~~bash
python tracker.py --file data/my_expenses.csv summary
~~~

Without <code>--month</code>, list and summary use all records. A nonexistent file is treated as an empty tracker, and the first add creates it.

## How the code works

| Function | Responsibility |
|---|---|
| make_expense | Validate and normalize one input record |
| read_expenses | Read CSV records into Expense objects |
| add_expense | Validate the existing file, then append a record |
| select_month | Keep records belonging to a YYYY-MM period |
| summarize | Sum amounts by category and overall |
| main | Parse command-line arguments and display results |

The storage format is intentionally readable:

~~~csv
date,category,amount,note
2025-03-01,food,18000.00,Coffee
~~~

The CSV module handles commas and quotation marks in notes. Dates must be real calendar dates in YYYY-MM-DD form. Categories are trimmed and converted to lowercase. Amounts must be positive, finite, no greater than one trillion, and expressible with at most two decimal places.

## Why Decimal?

Binary floating-point numbers cannot represent every decimal fraction exactly. This project constructs Decimal directly from the user's text so that 0.10 plus 0.20 is exactly 0.30.

The input is never converted to float first. Formatting to two decimals is for display; it is not a replacement for accurate arithmetic.

## Tests

~~~bash
python -m unittest discover -s tests -v
~~~

The tests cover exact totals, invalid input, quoted CSV fields, month filtering, persistence, and the handling of a malformed file. Tests use temporary directories and do not edit your real expense file.

## Privacy and limitations

The bundled sample data is fictional. Personal files under data are ignored by Git by default; only the sample is included. Check the files you stage before publishing personal records, especially if you choose a storage path outside data.

This is a single-user learning tool. It has no encryption, database, concurrent-write protection, bank connection, refunds, exchange-rate conversion, or automatic backups. Back up important records. If an existing CSV is malformed, the program stops instead of overwriting it.

## Practice exercises

1. Add a budget amount and calculate the remaining monthly budget.
2. Add a highest-expense command.
3. Export a category summary to another CSV file.
4. Add expense IDs, then implement deletion without confusing repeated records.
5. Explain when you would replace CSV storage with SQLite.

**Questions to be able to answer:** Why separate parsing from storage? Why use Decimal? How would you keep two simultaneous writes from interfering?

Read [tracker.py](tracker.py) from the validation functions down to main. You should be able to explain each step before adding a new feature.

## References

- [Python: csv](https://docs.python.org/3/library/csv.html)
- [Python: decimal](https://docs.python.org/3/library/decimal.html)
- [Python: argparse](https://docs.python.org/3/library/argparse.html)


## Validation and license

The project has been tested locally on Windows with Python 3.13. GitHub Actions checks Python 3.11 and 3.12; see the status badge at the top for the current result.

Code and the synthetic demonstration data are available under the [MIT License](LICENSE).
