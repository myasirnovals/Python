from CLIBankSystem.models.Account import Account


class Bank:
    def __init__(self, name):
        self.name = name
        self.accounts = {}

    def create_account(self, account_number, holder_name, initial_balance=0):
        if account_number not in self.accounts:
            new_account = Account(account_number, holder_name, initial_balance)
            self.accounts[account_number] = new_account
            print(f"Account created successfully for {holder_name}, Account number: {account_number}")
        else:
            print("Account with the given number already exists.")

    def get_account(self, account_number):
        return self.accounts.get(account_number)