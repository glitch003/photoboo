from photoboo.PhotoBooManager import PhotoBooManager
import time

image_filepath = "beatles.jpg"
# image_filepath = "original_1571629730.jpg"
# image_filepath = "22829408_10155695942842660_4876641366014296389_o.jpg"
# image_filepath = "adonis-moustache.jpg"

photo_boo = PhotoBooManager()

timestamp = round(time.time())
image = photo_boo.ghostify(image_filepath, timestamp)

print(image)