from photoboo.PhotoBooManager import PhotoBooManager


# image_filepath = "beatles.jpg"
image_filepath = "22829408_10155695942842660_4876641366014296389_o.jpg"
# image_filepath = "adonis-moustache.jpg"

photo_boo = PhotoBooManager()

image = photo_boo.ghostify(image_filepath)

print(image)