from unittest import TestCase
from akari.danbooru_helper import search_tag_category

class Test(TestCase):
    def test_search_tag_category(self):
        # Since I live in China Mainland, I have to use proxy
        proxies = {
            'http': '127.0.0.1:6666',
            'https': '127.0.0.1:6666',
        }
        result=search_tag_category("inui_toko",proxy=proxies)
        self.assertFalse(result is None,"result is none")
        print(result)
