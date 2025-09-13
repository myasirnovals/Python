from cv2 import imwrite

import cv2


def images_compress(img_file):
    img = cv2.imread(img_file)
    imwrite('compressed-2.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 0])
    print('image compressed successfully')

images_compress('image.jpg')
