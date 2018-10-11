from pathlib import Path
import base64
import string
Path().expanduser()


class PhotoManager:

    sql_connection = None
    table_name = "photoboo_photos"
    save_folder = "../../../images/"

    def __init__(self, sql_connection):
        self.sql_connection = sql_connection

    def __get_save_folder_path(self):
        save_folder = Path(__file__) / self.save_folder
        real_path = save_folder.resolve()
        if real_path.exists() is False:
            try:
                real_path.mkdir()
            except:
                f = open("/tmp/photo_api.log", "w+")
                f.write("Error: could not create folder: {}\n".format(
                    real_path.as_posix()
                ))
                f.write("===========================\n")
                f.close()
        return real_path

    def __save_image_to_disk(self, image_data, filename):
        path = self.__get_save_folder_path()
        file_path = path / filename
        try:
            image = base64.b64decode(image_data)
            f = open(file_path.as_posix(), "wb")
            f.write(image)
            f.close()
        except:
            f = open("/tmp/photo_api.log", "w+")
            f.write("Error: could save file: {}\n".format(
                file_path.as_posix()
            ))
            f.write("===========================\n")
            f.close()

    def __clean_filename(self, name):
        # taken from:
        # https://stackoverflow.com/a/295146/9193553
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        file_name = ''.join(c for c in name if c in valid_chars)
        return file_name

    def get_photo_by_id(self, id):
        cur = self.sql_connection.cursor()
        cleaned_id = self.sql_connection.escape(int(id))
        query = "SELECT `id`,`name`, TO_BASE64(`data`) as `base64_data`, `ctime` FROM `{}` WHERE `id`={};".format(
            self.table_name,
            cleaned_id
        )
        cur.execute(query)

        PHOTO_ID = 0
        PHOTO_NAME = 1
        PHOTO_DATA = 2
        PHOTO_CTIME = 3

        photo = {}
        for row in cur:
            path = self.__get_save_folder_path() / self.__clean_filename(row[PHOTO_NAME])
            photo = {
                "id": row[PHOTO_ID],
                "name": row[PHOTO_NAME],
                "data": row[PHOTO_DATA],
                "url": path.as_posix().replace(
                    "/var/www/20mission.org/www",
                    ""
                ),
                "ctime": int(row[PHOTO_CTIME].timestamp())
            }
        cur.close()
        return photo

    def get_random_photo(self):
        cur = self.sql_connection.cursor()
        query = "SELECT `id`,`name`, TO_BASE64(`data`) as `base64_data`, `ctime` FROM `{}` ORDER BY RAND() LIMIT 0,1;".format(
            self.table_name
        )
        cur.execute(query)

        PHOTO_ID = 0
        PHOTO_NAME = 1
        PHOTO_DATA = 2
        PHOTO_CTIME = 3

        photo = {}
        for row in cur:
            path = self.__get_save_folder_path() / self.__clean_filename(row[PHOTO_NAME])
            photo = {
                "id": row[PHOTO_ID],
                "name": row[PHOTO_NAME],
                "data": row[PHOTO_DATA],
                "url": path.as_posix().replace(
                    "/var/www/20mission.org/www",
                    ""
                ),
                "ctime": int(row[PHOTO_CTIME].timestamp())
            }
        cur.close()
        return photo

    def save_new_photo(self, name, data):
        cur = self.sql_connection.cursor()
        cleaned_name = self.sql_connection.escape(name)
        cleaned_data = self.sql_connection.escape(data)
        query = "INSERT INTO `photoboo_photos` (`name`,`data`) values ({},FROM_BASE64({}));".format(
            cleaned_name,
            cleaned_data
        )
        cur.execute(query)
        self.sql_connection.commit()
        filename = self.__clean_filename(name)
        self.__save_image_to_disk(data, filename)
        cur.close()

    def get_metadata_for_all_photos(self):
        cur = self.sql_connection.cursor()
        # FIXME: figure out if user is trying to get a particular photo
        query = "SELECT `id`,`name`,`ctime` from `{}` ORDER BY `ctime` DESC;".format(
            self.table_name
        )
        cur.execute(query)

        PHOTO_ID = 0
        PHOTO_NAME = 1
        PHOTO_CTIME = 2

        photos = []

        images_folder_path = self.__get_save_folder_path()
        for row in cur:
            path = images_folder_path / self.__clean_filename(row[PHOTO_NAME])
            photo = {
                "id": row[PHOTO_ID],
                "name": row[PHOTO_NAME],
                "url": path.as_posix().replace(
                    "/var/www/20mission.org/www",
                    ""
                ),
                "ctime": int(row[PHOTO_CTIME].timestamp())
            }
            photos.append(photo)

        cur.close()
        return photos
