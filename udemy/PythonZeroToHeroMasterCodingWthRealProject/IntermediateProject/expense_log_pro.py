import csv


class ExpenseTracker:
    def __init__(self):
        self.expenses = []
        self.filename = 'expenses.csv'

    def add_expense(self, category, amount):
        self.expenses.append({
            'category': category,
            'amount': amount
        })

        self.save_to_file()

    def display_expenses(self):
        self.load_from_file()

        if not self.expenses:
            print('No expenses recorded yet!')
        else:
            print('Expenses list: ')
            for expense in self.expenses:
                print(f'Category: {expense["category"]}, Amount: {expense["amount"]}')

    def save_to_file(self):
        with open(self.filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['category', 'amount'])
            writer.writeheader()
            writer.writerows(self.expenses)

    def load_from_file(self):
        try:
            with open(self.filename, 'r') as file:
                reader = csv.DictReader(file)
                self.expenses = list(reader)
        except FileNotFoundError:
            pass


expense_tracker = ExpenseTracker()

while True:
    print('\nExpense Tracker Menu: ')
    print('1. Add Expense')
    print('2. Display Expenses')
    print('3. Exit')

    choice = input('Enter your choice (1/2/3): ')

    if choice == '1':
        category = input('Enter the expense category: ')
        amount = float(input('Enter the expense amount: '))
        expense_tracker.add_expense(category, amount)
        print('Expense added successfully!')
    elif choice == '2':
        expense_tracker.display_expenses()
    elif choice == '3':
        print('Exiting the program...')
        break
    else:
        print('Invalid choice! Please enter a valid choice.')
