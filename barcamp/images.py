import cloudinary
import cloudinary.uploader

def upload_image(image_path, image_name):
    uploaded = cloudinary.uploader.upload(image_path, public_id="image_name")
    return uploaded['url']
