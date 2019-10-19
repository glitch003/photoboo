from photoboo.PhotoBooManager import PhotoBooManager


# image_filepath = "beatles.jpg"
image_filepath = "adonis-moustache.jpg"

photo_boo = PhotoBooManager()

image = photo_boo.ghostify(image_filepath)

print(image)