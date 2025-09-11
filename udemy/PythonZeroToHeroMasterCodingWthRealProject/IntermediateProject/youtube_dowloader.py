import pytube

video_url = 'https://youtu.be/sGzYDL9otb8?si=CV0qE7zBBlVlBp-T'

try:
    video = pytube.YouTube(video_url).streams.first()
    video.download('H://Downloads')
    print('success: the file downloaded successfully!')
except Exception as e:
    print('error: something went wrong!')
    print(f'error message: {e}')
