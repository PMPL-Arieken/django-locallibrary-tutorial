from .base import FunctionalTest
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User
import time

class TestBorrowed(FunctionalTest):

    def setUp(self):
        super().setUp()
        super().setUpBooks()

    def tearDown(self):
        return super().tearDown()

    def login(self, user):
        self.browser.get(self.live_server_url + "/catalog/borrowed/")
        username = self.browser.find_element_by_css_selector('input[name=username]')
        password = self.browser.find_element_by_css_selector('input[name=password]')
        submit = self.browser.find_element_by_css_selector('input[type=submit]')

        username.send_keys(user['username'])
        password.send_keys(user['password'])
        submit.send_keys(Keys.ENTER)
        time.sleep(1)

    def test_borrowed_user(self):
        self.login(self.user)
        self.assertEqual(self.browser.title, '403 Forbidden')


    def test_borrowed_admin(self):
        self.login(self.admin)
        self.assertEqual(self.browser.title, 'Local Library')

        lis = self.browser.find_elements_by_css_selector('div.col-sm-10 ul li')
        self.assertEqual(len(lis), 10)

        for li in lis[:10]:
            hrefs = li.find_elements_by_tag_name('a')
            if len(hrefs) > 0:
                href = hrefs[0]
                self.assertEqual(href.text, "Book Title")
