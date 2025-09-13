from PIL import Image

import os


def convert_image_to_jpg(image_path):
    try:
        image = Image.open(image_path)
        if image.format != 'JPEG':
            output_path = os.path.splitext(image_path)[0] + '.jpg'
            image = image.convert('RGB')
            image.save(output_path, 'JPEG')
            print(f'conversion successful, image saved as {output_path}')
        else:
            print('image is already in JPEG format.')
    except OSError:
        print(f'Conversion failed for {image_path}')


image_path = 'potret_burung_bangau.png'

convert_image_to_jpg(image_path)
