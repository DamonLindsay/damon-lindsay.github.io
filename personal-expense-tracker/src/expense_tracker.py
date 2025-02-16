import json
import os
from datetime import datetime


class ExpenseTracker:
    def __init__(self, data_file='expenses.json'):
        self.data_file = data_file
        self.expenses = []
        self.load_expenses()

    def add_expense(self, amount, category, description=''):
        expense = {
            'amount': amount,
            'category': category,
            'description': description,
            'date': datetime.now().isoformat()
        }
        self.expenses.append(expense)
        self.save_expenses()

    def load_expenses(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.expenses = json.load(f)
        else:
            self.expenses = []

    def save_expenses(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.expenses, f, indent=4)

    def list_expenses(self):
        return self.expenses
