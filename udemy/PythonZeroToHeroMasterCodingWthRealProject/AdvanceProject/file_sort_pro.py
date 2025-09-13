import os
import shutil


def organize_files(directory):
    file_types = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.bmp', '.svg', '.webp'],
        'documents': ['.pdf', '.docx', '.doc', '.txt', '.pptx', '.ppt', '.xlsx', '.xls', '.odt', '.csv'],
        'archives': ['.zip', '.rar', '.tar', '.gz', '.7z'],
        'audio': ['.mp3', '.wav', '.m4a', '.flac', 'aac', '.ogg'],
        'video': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'],
        'scripts': ['.py', 'js', '.html', '.css', '.java', '.cpp', '.c', '.sh', '.json', '.xml'],
        'executables': ['.exe', '.msi', '.dmg', '.app', '.deb', '.rpm'],
        'fonts': ['.ttf', '.otf', '.woff', '.woff2'],
        'other': []
    }

    for subdir in file_types:
        os.makedirs(os.path.join(directory, subdir), exist_ok=True)

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path):
            file_ext = os.path.splitext(filename)[1].lower()

            file_moved = False

            for category, extensions in file_types.items():
                if file_ext in extensions:
                    shutil.move(file_path, os.path.join(directory, category, filename))
                    file_moved = True
                    break

            if not file_moved:
                shutil.move(file_path, os.path.join(directory, 'other', filename))

    print('file organization completed')

directory_path = 'H://Downloads'
organize_files(directory_path)
