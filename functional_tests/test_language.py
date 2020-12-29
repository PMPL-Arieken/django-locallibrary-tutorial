import time
from .base import FunctionalTest
from catalog.models import Author, Language
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User

class TestLanguagePage(FunctionalTest):

    def setUp(self):
        super().setUp()
        super().setUpBooks()

    def test_language_page_anonymous(self):
        self.browser.get(self.live_server_url + '/catalog/languages/')
        self.assertEqual(self.browser.current_url, self.live_server_url + '/accounts/login/?next=/catalog/languages/')

    def test_language_page_empty(self):
        Language.objects.all().delete()
        self.login(self.admin)
        self.browser.get(self.live_server_url + '/catalog/languages/')
        self.assertIn('There are no languages available', self.browser.find_element_by_tag_name('body').text)

    def test_language_page_not_empty(self):
        self.login(self.admin)
        self.browser.get(self.live_server_url + '/catalog/languages/')
        self.assertIn('English', self.browser.find_element_by_tag_name('body').text)
