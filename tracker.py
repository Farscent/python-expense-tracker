"""A small CSV expense tracker using only Python's standard library."""
import argparse
import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = ["date", "category", "amount", "note"]

@dataclass(frozen=True)
class Expense:
    date: date
    category: str
    amount: Decimal
    note: str = ""

def parse_date(value):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("Use dates in YYYY-MM-DD format.")
    return date.fromisoformat(value)

def parse_amount(value):
    try:
        amount = Decimal(value)
    except InvalidOperation as error:
        raise ValueError("Amount must be a number such as 18000 or 18000.50.") from error
    if not amount.is_finite() or amount <= 0 or amount > Decimal("1000000000000"):
        raise ValueError("Amount must be finite, positive, and at most 1 trillion.")
    if amount != amount.quantize(Decimal("0.01")):
        raise ValueError("Use at most two decimal places.")
    return amount.quantize(Decimal("0.01"))

def make_expense(day, category, amount, note=""):
    category = category.strip().lower()
    if not category or len(category) > 40:
        raise ValueError("Category must contain 1 to 40 characters.")
    return Expense(parse_date(day), category, parse_amount(amount), note.strip())

def read_expenses(path):
    path = Path(path)
    if not path.exists():
        return []
    expenses = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"CSV header must be: {','.join(FIELDS)}")
        for line, row in enumerate(reader, start=2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Malformed CSV record near line {line}.")
            try:
                expenses.append(make_expense(row["date"], row["category"], row["amount"], row["note"]))
            except ValueError as error:
                raise ValueError(f"Invalid record near line {line}: {error}") from error
    return expenses

def add_expense(path, expense):
    path = Path(path)
    # Validate an existing file before appending, so errors do not corrupt its records.
    read_expenses(path)
    is_new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow({"date": expense.date.isoformat(), "category": expense.category,
                         "amount": str(expense.amount), "note": expense.note})

def select_month(expenses, month=None):
    if month is None:
        return expenses
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}", month):
        raise ValueError("Use months in YYYY-MM format.")
    parse_date(month + "-01")
    return [expense for expense in expenses if expense.date.strftime("%Y-%m") == month]

def summarize(expenses):
    totals = defaultdict(lambda: Decimal("0.00"))
    for expense in expenses:
        totals[expense.category] += expense.amount
    return dict(sorted(totals.items())), sum(totals.values(), Decimal("0.00"))

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=ROOT / "data/expenses.csv",
                        help="CSV path; place this option before the command.")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="Append one expense.")
    add.add_argument("--date", default=date.today().isoformat())
    add.add_argument("--category", required=True)
    add.add_argument("--amount", required=True)
    add.add_argument("--note", default="")
    for name in ["list", "summary"]:
        command = commands.add_parser(name)
        command.add_argument("--month", help="Optional YYYY-MM filter.")
    args = parser.parse_args(argv)
    try:
        if args.command == "add":
            expense = make_expense(args.date, args.category, args.amount, args.note)
            add_expense(args.file, expense)
            print(f"Added {expense.category}: IDR {expense.amount:,.2f}")
            return
        expenses = select_month(read_expenses(args.file), args.month)
        if args.command == "list":
            if not expenses:
                print("No expenses found.")
            for expense in sorted(expenses, key=lambda item: item.date):
                print(f"{expense.date} | {expense.category:<16} | IDR {expense.amount:>12,.2f} | {expense.note}")
        else:
            categories, total = summarize(expenses)
            for category, amount in categories.items():
                print(f"{category:<16} IDR {amount:>12,.2f}")
            print(f"{'TOTAL':<16} IDR {total:>12,.2f} ({len(expenses)} expenses)")
    except (ValueError, OSError) as error:
        parser.exit(2, f"Error: {error}\n")

if __name__ == "__main__":
    main()
