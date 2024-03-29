from photoboo.PhotoBooManager import PhotoBooManager
import time

# image_filepath = "beatles.jpg"
image_filepath = "original_1571629730.jpg"
# image_filepath = "adonis-moustache.jpg"

photo_boo = PhotoBooManager()

timestamp = round(time.time())
print("ghosting...")
image = photo_boo.ghostify(cv2.imread(image_filepath, cv2.IMREAD_GRAYSCALE), timestamp)
print("took {} seconds to ghost".format(round(time.time()) - timestamp))

print(image)