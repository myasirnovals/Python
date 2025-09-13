import PIL.Image as Image
import PIL.ImageFilter as ImageFilter
import PIL.ImageOps as ImageOps
import PIL.ImageEnhance as ImageEnhance


def crop_image(image, start_x, start_y, end_x, end_y):
    return image.crop((start_x, start_y, end_x, end_y))


def resize_image(image, width, height):
    return image.resize((width, height))


def flip_image(image):
    return image.transpose(Image.FLIP_LEFT_RIGHT)


def rotate_image(image, degrees):
    return image.rotate(degrees)


def compress_image(image, save_path, quality):
    return image.save(save_path, optimize=True, quality=quality)


def blur_image(image):
    return image.filter(ImageFilter.BLUR)


def sharpen_image(image):
    return image.filter(ImageFilter.SHARPEN)


def adjust_brightness(image, brightness):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(brightness)


def adjust_contrast(image, contrast):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(contrast)


def add_filters(image):
    image = ImageOps.grayscale(image)
    image = ImageOps.invert(image)
    image = ImageOps.posterize(image, 4)
    return image


def optimize_image(image):
    # image = crop_image(image, 50, 50, 700, 700)
    # image = resize_image(image, 200, 200)
    # image = flip_image(image)
    # image = rotate_image(image, 45)
    # compress_image(image, 'optimized-image4.jpg', 10)
    # image = blur_image(image)
    # image = sharpen_image(image)
    # image = adjust_brightness(image, 1.5)
    # image = adjust_contrast(image, 1.5)
    image = add_filters(image)

    return image

img = Image.open('image.jpg')
optimize_img = optimize_image(img)
optimize_img.save('optimized-image9.jpg')
