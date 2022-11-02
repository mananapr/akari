import os.path
import sqlite3
import sys
from pathlib import Path
import gc

'''
    connection_pool save the OBJECT of the certain class
'''
connection_pool = {"tag": set()}

data_dir = str(Path.home()) + '/.config/akari'

"""



"""

class tag_database():

    conn: sqlite3.Connection
    db: sqlite3.Cursor

    def __del__(self):
        try:
            self.db.close()
            self.conn.close()
            connection_pool["tag"].remove(self.conn)
        except Exception as exception:
            print(exception)
        return

    def __init__(self):
        database_path = os.path.join(data_dir , "tag.db")
        try:
            if not os.path.isfile(database_path):
                self.conn = sqlite3.connect(database_path)
                print("create new tag table")
                self.conn.execute('''
                    CREATE TABLE tag
                    ( id        INTEGER PRIMARY KEY AUTOINCREMENT,
                      name      TEXT NOT NULL UNIQUE ,
                      category  TEXT
                    );''')
                self.conn.commit()
            else:
                self.conn = sqlite3.connect(database_path)

        except sqlite3.Error as err:
            self.conn.rollback()
            print(err)
            sys.exit(2)
        else:
            connection_pool["tag"].add(self.conn)

        self.db = self.conn.cursor()

    def add_tag(self, tag_name: str, category: str):
        try:
            self.db.execute('''
                INSERT OR IGNORE INTO tag(`name`,`category`)
                VALUES (?, ?);
            ''', [tag_name, category])
            self.conn.commit()
        except sqlite3.Error as err:
            self.conn.rollback()
            print(err)
            sys.exit(2)

    def query_tag_category(self, tag_name: str):
        try:
            self.db.execute('''
                SELECT category
                FROM tag
                WHERE tag.name = ?;
            ''', [tag_name])
            return self.db.fetchone()[0]
        except sqlite3.Error as err:
            print(err)
            sys.exit(2)

    '''
        WARNING: 
            Clear the database by remove the database file
    '''

    @staticmethod
    def clean_db():
        for _,tag_db in enumerate(connection_pool["tag"]):
            if tag_db is not None:
                tag_db.close()

        if os.path.isfile(os.path.join(data_dir , "tag.db")):
            os.remove(os.path.join(data_dir , "tag.db"))

