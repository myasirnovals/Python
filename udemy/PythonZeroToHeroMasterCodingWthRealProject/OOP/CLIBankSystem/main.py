from CLIBankSystem.models.Bank import Bank

bank = Bank("IUPAC Bank")

# create an account
alice_account = bank.create_account(10001, "Alice", 1000)
bob_account = bank.create_account(10002, "Bob")

# accessing an account
alice_account = bank.get_account(10001)
bob_account = bank.get_account(10002)

# making a transaction
alice_account.deposit(500)
alice_account.withdraw(200)

bob_account.deposit(1000)
bob_account.withdraw(300)

# display transaction history and balances
alice_account.display_transaction_history()
alice_account.display_balance()

bob_account.display_transaction_history()
bob_account.display_balance()