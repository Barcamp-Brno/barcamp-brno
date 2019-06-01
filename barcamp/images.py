from math import floor

import cloudinary
import cloudinary.uploader
from PIL import Image

def square_crop_thumbnail(image_path, max_width=1000, max_height=1000):
    image = Image.open(image_path) # may throw OSError when not an image uploaded
    (width, height) = image.size
    if height < max_height or width < max_width:
        return False

    # compute biggest square in the middle
    offset = floor(abs(width - height) / 2)
    left = 0 if width < height else 0 + offset
    right = width if width < height else width - offset
    upper = 0 if width > height else 0 + offset
    lower = height if width > height else height - offset

    # crop & resize image to max_width, max_height dimensions
    cropped_image = image.crop((left, upper, right, lower))
    cropped_image.thumbnail((max_width, max_height))
    cropped_image.save(image_path, "JPEG")
    return True

def upload_image(image_path, image_name):
    uploaded = cloudinary.uploader.upload(image_path, public_id=image_name)
    return uploaded['url']
