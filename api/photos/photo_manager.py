class PhotoManager:

    sql_connection = None
    table_name = "photoboo_photos"

    def __init__(self, sql_connection):
        self.sql_connection = sql_connection

    def get_photo_by_id(self, id):
        cur = self.sql_connection.cursor()
        cleaned_id = self.sql_connection.escape(int(id))
        query = "SELECT `id`,`name`, TO_BASE64(`data`) as `base64_data`, `ctime` FROM `{}` WHERE `id`={};".format(
            self.table_name;
            cleaned_id
        )
        cur.execute(query)
        
        PHOTO_ID = 0
        PHOTO_NAME = 1
        PHOTO_DATA = 3
        PHOTO_CTIME = 4

        photo = {}
        for row in cur:
            photo = {
                "id": row[PHOTO_ID],
                "name": row[PHOTO_NAME],
                "data": row[PHOTO_DATA],
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
            photo = {
                "id": row[PHOTO_ID],
                "name": row[PHOTO_NAME],
                "data": row[PHOTO_DATA],
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
        print("query: {}".format(query))
        cur.execute(query)
        self.sql_connection.commit()
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

        for row in cur:
            photo = {
                "id": row[PHOTO_ID],
                "name": row[PHOTO_NAME],
                "ctime": int(row[PHOTO_CTIME].timestamp())
            }
            photos.append(photo)

        cur.close()
        return photos
