import os
import shutil


def backup_and_sync(source_folder, backup_folder):
    for root, _, files in os.walk(source_folder):
        for file in files:
            source_path = os.path.join(root, file)
            backup_path = os.path.join(backup_folder, root.replace(source_folder, ""), file)

            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(source_path, backup_path)

    for root, _, files in os.walk(backup_folder):
        for file in files:
            backup_path = os.path.join(root, file)
            source_path = os.path.join(source_folder, root.replace(backup_folder, ""), file)

            if not os.path.exists(source_path):
                os.remove(backup_path)

source_folder = "H://Documents//sppt"
backup_folder = "H://Documents//Backup"

backup_and_sync(source_folder, backup_folder)