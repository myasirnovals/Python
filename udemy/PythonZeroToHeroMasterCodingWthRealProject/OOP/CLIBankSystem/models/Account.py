from CLIBankSystem.models.Transaction import Transaction


class Account:
    def __init__(self, account_number, holder_name, balance=0):
        self.account_number = account_number
        self.holder_name = holder_name
        self.balance = balance
        self.transactions = []

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.transactions.append(Transaction(amount, "Deposit"))
            print(f"Deposit of ${amount} Successful. New balance: ${self.balance}")
        else:
            print("Invalid amount. Deposit failed.")

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.transactions.append(Transaction(amount, "Withdrawal"))
            print(f"Withdrawal of ${amount} Successful. New balance: ${self.balance}")
        else:
            print("Invalid withdrawal amount or insufficient funds.")

    def display_transaction_history(self):
        print("\nTransaction History:")
        for transaction in self.transactions:
            print(f"${transaction.amount} {transaction.transaction_type}")

    def display_balance(self):
        print(f"\nCurrent Balance for Account {self.account_number}: ${self.balance}")
