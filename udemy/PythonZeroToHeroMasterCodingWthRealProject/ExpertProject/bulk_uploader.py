from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

google_auth = GoogleAuth()
drive_app = GoogleDrive(google_auth)

upload_list = ['sample.pdf', 'sample_background.jpg']

for file_to_upload in upload_list:
    file = drive_app.CreateFile({
        'parents': [{
            'id': ''
        }]
    })

    file.SetContentFile(file_to_upload)
    file.Upload()
    print(f'{file_to_upload} uploaded successfully!')