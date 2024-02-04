import sqlite3
import logging

logger = logging.getLogger('images')
logger.setLevel(logging.DEBUG)

# This class will handle the DB operations.
# - Creating and dropping the main table
# - Inserting data from an array provided
# - Selecting one or more images, with the depth parameter
class DbManager:
    def __init__(self):
        self.con = sqlite3.connect("images.db")
        self.cur = self.con.cursor()
        self.initialize_db()

    def initialize_db(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS images(depth INTEGER PRIMARY KEY, image_data TEXT)")
        logger.debug("DB initialized")

    def insert_images(self, images):
        self.cur.executemany("REPLACE INTO images VALUES(?, ?)", images)
        self.con.commit()
        
    def get_image(self, depth: int):
        res = self.cur.execute("SELECT depth, image_data FROM images WHERE depth = ?", [depth])
        result = res.fetchone()
        if result and len(result) > 0:
            return result[1]
        return []
    
    def get_images(self, depth_min, depth_max):
        res = self.cur.execute("SELECT depth, image_data FROM images WHERE depth BETWEEN ? AND ?", [depth_min, depth_max])
        return res.fetchall()

    def drop_table(self):
        self.cur.execute("DROP TABLE IF EXISTS images")
