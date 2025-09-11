import cv2
import sys

face_cascade = cv2.CascadeClassifier('face_detector.xml')
img = cv2.imread('1710373864468.jpg')

if img is None:
    print("Error: Gambar tidak ditemukan atau tidak bisa dibaca.")
    print("Pastikan '1710373864468.jpg' ada di folder yang sama dengan skrip.")
    sys.exit()

faces = face_cascade.detectMultiScale(img, 1.1, 4)

for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

cv2.imwrite('detected_faces.jpg', img)
print('successfully saved!')
