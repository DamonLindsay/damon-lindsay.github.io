from pydoc import describe

from unicodedata import category

from expense_tracker import ExpenseTracker


def main():
    tracker = ExpenseTracker()
    while True:
        print('\nPersonal Expenses Tracker')
        print('1. Add Expense')
        print('2. List Expense')
        print('3. Exit')
        choice = input('Enter your choice: ')
        if choice == '1':
            try:
                amount = float(input('Enter amount: '))
            except ValueError:
                print('Invalid input. Please enter a number.')
                continue
            category = input('Enter category: ')
            description = input('Enter description (optional): ')
            tracker.add_expense(amount, category, description)
            print('Expense added successfully.')
        elif choice == '2':
            expenses = tracker.list_expenses()
            if expenses:
                for expense in expenses:
                    print(f"{expense['date']} - {expense['category']}: {expense['amount']} - {expense['description']}")
                else:
                    print("No expenses recorded.")
            elif choice == '3':
                print('Exiting.')
                break
            else:
                print("Invalid choice.  Please select again.")


if __name__ == '__main__':
    main()
