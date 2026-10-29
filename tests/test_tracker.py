import contextlib
import io
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from tracker import ROOT, add_expense, main, make_expense, parse_amount, parse_date, read_expenses, select_month, summarize

class TrackerTests(unittest.TestCase):
    def test_money_is_exact(self):
        expenses = [make_expense("2025-03-01", "food", "0.10"),
                    make_expense("2025-03-01", "food", "0.20")]
        _, total = summarize(expenses)
        self.assertEqual(total, Decimal("0.30"))

    def test_invalid_inputs(self):
        for value in ["0", "-1", "NaN", "Infinity", "1.001", "abc"]:
            with self.assertRaises(ValueError):
                parse_amount(value)
        for value in ["2025-02-30", "03/01/2025", "20250301"]:
            with self.assertRaises(ValueError):
                parse_date(value)
        with self.assertRaises(ValueError):
            make_expense("2025-01-01", " ", "10")

    def test_csv_round_trip_preserves_commas_and_quotes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "expenses.csv"
            expense = make_expense("2025-03-01", " Food ", "18000", 'Coffee, "large"')
            add_expense(path, expense)
            add_expense(path, expense)
            self.assertEqual(read_expenses(path), [expense, expense])

    def test_monthly_totals_exclude_other_months(self):
        expenses = read_expenses(ROOT / "data/sample_expenses.csv")
        categories, total = summarize(select_month(expenses, "2025-03"))
        self.assertEqual(total, Decimal("143000.00"))
        self.assertEqual(categories["food"], Decimal("43000.00"))
        self.assertEqual(summarize(select_month(expenses, "2026-01"))[1], Decimal("0.00"))

    def test_corrupt_file_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "expenses.csv"
            content = "incorrect,header\n1,2\n"
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(ValueError):
                add_expense(path, make_expense("2025-03-01", "food", "10"))
            self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_cli_uses_persistent_storage(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()) as output:
            path = str(Path(directory) / "expenses.csv")
            main(["--file", path, "add", "--date", "2025-03-01", "--category", "food", "--amount", "18000"])
            main(["--file", path, "summary", "--month", "2025-03"])
            self.assertIn("18,000.00", output.getvalue())
            self.assertIn("(1 expenses)", output.getvalue())

if __name__ == "__main__":
    unittest.main()
