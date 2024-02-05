import sqlite3
import logging

# Set up logger
logger = logging.getLogger('images')
logger.setLevel(logging.DEBUG)

class DbManager:
    def __init__(self, db_name="images.db"):
        self.db_name = db_name
        self._connect_db()

    def _connect_db(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self._initialize_db()

    def _initialize_db(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS images(depth INTEGER PRIMARY KEY, image_data TEXT)")
        logger.debug("Database initialized")

    def insert_images(self, images):
        self.cursor.executemany("REPLACE INTO images VALUES(?, ?)", images)
        self.connection.commit()

    def get_image(self, depth: int):
        query = "SELECT depth, image_data FROM images WHERE depth = ?"
        res = self.cursor.execute(query, [depth])
        result = res.fetchone()
        return result[1] if result else []

    def get_images(self, depth_min, depth_max):
        query = "SELECT depth, image_data FROM images WHERE depth BETWEEN ? AND ?"
        res = self.cursor.execute(query, [depth_min, depth_max])
        return res.fetchall()

    def drop_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS images")

    def close_connection(self):
        self.connection.close()
