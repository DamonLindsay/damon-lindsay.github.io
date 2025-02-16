import sys
import os
import unittest

# Add the project route (parent directory) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.expense_tracker import ExpenseTracker


class TestExpenseTracker(unittest.TestCase):
    def setUp(self):
        # Use a temporary file for testing tyo avoid interfering with production data.
        self.test_file = 'test_expenses.json'
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.tracker = ExpenseTracker(data_file=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_expense(self):
        self.tracker.add_expense(20.5, 'Food', 'Lunch')
        self.assertEqual(len(self.tracker.expenses), 1)
        expense = self.tracker.expenses[0]
        self.assertEqual(expense['amount'], 20.5)
        self.assertEqual(expense['category'], 'Food')
        self.assertEqual(expense['description'], 'Lunch')

    def test_save_and_load_expense(self):
        self.tracker.add_expense(50, 'Transport', 'Bus fare')
        # Create a new instance to check if data persists
        new_tracker = ExpenseTracker(data_file=self.test_file)
        self.assertEqual(len(self.tracker.expenses), 1)
        expense = new_tracker.expenses[0]
        self.assertEqual(expense['amount'], 50)


if __name__ == '__main__':
    unittest.main()
