# Python Expense Tracker

[![Tests](https://github.com/Farscent/python-expense-tracker/actions/workflows/tests.yml/badge.svg)](https://github.com/Farscent/python-expense-tracker/actions/workflows/tests.yml)

A command-line application for recording expenses in CSV and producing category and monthly summaries. It uses Python's standard library and Decimal arithmetic to preserve exact monetary totals.

## Features

- Append expense records with dates, categories, amounts, and notes.
- List records chronologically and filter by month.
- Summarize category totals and overall spending.
- Validate input and existing CSV records before appending.
- Store data in a readable format without a database or external services.

## Example output

The included fictional sample contains five March expenses totaling **IDR 143,000.00**.

| Category | March total (IDR) |
|---|---:|
| Education | 45,000.00 |
| Entertainment | 30,000.00 |
| Food | 43,000.00 |
| Transport | 25,000.00 |
| **Total** | **143,000.00** |

The sample also contains an April record, which is excluded by the March filter.

## Installation

Requires **Python 3.11–3.13**. No third-party packages are needed.

~~~bash
git clone https://github.com/Farscent/python-expense-tracker.git
cd python-expense-tracker
python tracker.py --help
~~~

## Usage

Inspect the sample records:

~~~bash
python tracker.py --file data/sample_expenses.csv list
python tracker.py --file data/sample_expenses.csv summary --month 2025-03
~~~

Record and summarize expenses in the default local file:

~~~bash
python tracker.py add --date 2025-03-01 --category food --amount 18000 --note "Coffee"
python tracker.py add --date 2025-03-02 --category transport --amount 5000 --note "Bus"
python tracker.py list --month 2025-03
python tracker.py summary --month 2025-03
~~~

The default file is <code>data/expenses.csv</code>. The first add creates it if needed. Omitting the date uses today; omitting the month includes all records. Each add command appends a new expense.

A custom <code>--file</code> option must precede the command:

~~~bash
python tracker.py --file data/my_expenses.csv summary
~~~

## Data format and validation

~~~csv
date,category,amount,note
2025-03-01,food,18000.00,Coffee
~~~

Dates must be valid calendar dates in YYYY-MM-DD format. Categories are trimmed and lowercased. Amounts must be positive, finite, no greater than one trillion, and expressible with at most two decimal places. The CSV module preserves commas and quotes in notes.

Amounts are parsed directly from text into Decimal, avoiding an intermediate float conversion. All records are assumed to use a single currency; the displayed currency is IDR.

## Implementation

[tracker.py](tracker.py) separates validation, storage, filtering, aggregation, and command-line handling. An immutable Expense dataclass represents each record.

| Function | Responsibility |
|---|---|
| make_expense | Validate and normalize input |
| read_expenses | Load and validate CSV records |
| add_expense | Append a validated record |
| select_month | Filter by YYYY-MM |
| summarize | Calculate category totals and overall spending |
| main | Parse arguments and display results |

## Limitations and data handling

The application supports single-user local storage. It does not provide concurrent-write protection, encryption, refunds, currency conversion, bank integration, or automatic backups.

A malformed CSV stops processing instead of being overwritten. Personal files under data are ignored by Git; only the fictional sample is included. Files stored outside that directory require their own version-control exclusions.

## Validation

Tests cover exact decimal totals, invalid input, quoted CSV fields, monthly filtering, file persistence, and malformed-file handling. File tests use temporary directories.

~~~bash
python -m unittest discover -s tests -v
~~~

GitHub Actions runs the checks on Python 3.11 and 3.12. The project has also been verified on Windows with Python 3.13.

## References

- [Python: csv](https://docs.python.org/3/library/csv.html)
- [Python: decimal](https://docs.python.org/3/library/decimal.html)
- [Python: argparse](https://docs.python.org/3/library/argparse.html)

## License

Code and synthetic demonstration data are available under the [MIT License](LICENSE).
