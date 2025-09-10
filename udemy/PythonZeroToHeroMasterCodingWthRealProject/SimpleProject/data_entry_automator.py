import pandas as pd


def automate_data_entry(data, file_path):
    try:
        try:
            existing_data = pd.read_csv(file_path)
        except FileNotFoundError:
            existing_data = pd.DataFrame()

        new_data = pd.DataFrame(data)
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        combined_data.to_csv(file_path, index=False)
        print("Data entry successful.")
    except Exception as e:
        print(f"An error occurred: {e}")


data_to_enter = [
    {'name': 'John', 'age': 30, 'city': 'New York'},
    {'name': 'Mary', 'age': 25, 'city': 'Los Angeles'},
    {'name': 'Bob', 'age': 40, 'city': 'Chicago'},
    {'name': 'Alice', 'age': 20, 'city': 'Houston'}
]

csv_file_path = 'data.csv'
automate_data_entry(data_to_enter, csv_file_path)
