import os.path
from unittest import TestCase
from akari import db


class Testtag_database(TestCase):
    def test_add_tag(self):
        tag_db = db.tag_database()
        tag_db.add_tag("inui_toko","character")


    def test_query_tag_category(self):
        tag_db = db.tag_database()
        print(tag_db.query_tag_category("inui_toko"))
        self.assertEqual(tag_db.query_tag_category("inui_toko"), "character", "wrong")

    def test_clear_db_no_connection(self):
        with self.subTest("Case 1: No connection"):
            db.tag_database.clean_db()
            self.assertFalse(os.path.isfile(os.path.join(db.data_dir , "tag.db")))

        with self.subTest("Case 2: Multiple open connection"):
            tag_db1 = db.tag_database()
            tag_db2 = db.tag_database()
            tag_db3 = db.tag_database()
            tag_db1.add_tag("t1","test")
            tag_db2.add_tag("t2", "test")
            tag_db3.add_tag("t3", "test")
            db.tag_database.clean_db()
            self.assertFalse(os.path.isfile(os.path.join(db.data_dir , "tag.db")))
