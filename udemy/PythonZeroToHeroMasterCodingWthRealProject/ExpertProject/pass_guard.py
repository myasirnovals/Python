from cryptography.fernet import Fernet

import os
import json


class PasswordManager:
    def __init__(self):
        self.key = self.load_key()
        self.accounts = self.load_accounts()

    def load_key(self):
        key_file = 'key.key'

        if os.path.exists(key_file):
            with open(key_file, 'rb') as file:
                return file.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as file:
                file.write(key)

            return key

    def load_accounts(self):
        accounts_file = 'accounts.json'
        if os.path.exists(accounts_file):
            with open(accounts_file, 'rb') as file:
                cipher_suit = Fernet(self.key)
                encrypted_data = file.read()
                decrypted_data = cipher_suit.decrypt(encrypted_data)
                return json.loads(decrypted_data)
        else:
            return {}

    def save_accounts(self):
        accounts_file = 'accounts.json'
        with open(accounts_file, 'wb') as file:
            cipher_suit = Fernet(self.key)
            data = json.dumps(self.accounts).encode()
            encrypted_data = cipher_suit.encrypt(data)
            file.write(encrypted_data)

    def add_account(self, account_name, username, account_password):
        self.accounts[account_name] = {
            'username': username,
            'password': account_password
        }

        self.save_accounts()
        print(f'Account {account_name} added successfully!')

    def get_password(self, account_name):
        if account_name in self.accounts:
            return self.accounts[account_name]['password']
        else:
            return 'Account not found!'


password_manager = PasswordManager()
password_manager.add_account(
    input('Enter account name: '),
    input('Enter username: '),
    input('Enter password: ')
)

password = password_manager.get_password(input('Enter account name: '))
print(f'Password is: {password}')