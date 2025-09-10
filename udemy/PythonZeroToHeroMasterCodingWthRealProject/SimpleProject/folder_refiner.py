import os

os.chdir('H://OneDrive//Pictures//Screenshots')
for file in os.listdir():
    if file.endswith('.png'):
        os.remove(file)
        print('all files ends with .png deleted!')