import datetime
import time
from .base import FunctionalTest
from django.utils import timezone
from catalog.models import Author, Book, BookInstance, Genre, Language
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User
class TestAuthorPage(FunctionalTest):

    def setUp(self):
        super().setUp()

        self.user = {
            'username': 'testuser', 
            'password': '1X<ISRUkw+tuK',
            'is_staff': True,
            'is_active' : True,
            'is_superuser' : True,
        }

        User.objects.create_user(**self.user).save()

    def login(self, user):
        self.browser.get(self.live_server_url + "/accounts/login/")
        username = self.browser.find_element_by_css_selector('input[name=username]')
        password = self.browser.find_element_by_css_selector('input[name=password]')
        submit = self.browser.find_element_by_css_selector('input[type=submit]')

        username.send_keys(user['username'])
        password.send_keys(user['password'])

        submit.send_keys(Keys.ENTER)
        time.sleep(1)

    def test_author_page_empty(self):
        self.browser.get(self.live_server_url + '/catalog/authors')
        self.assertEqual(self.browser.title, 'Local Library')
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual(header_text, 'Author List')
        
        list_text = self.browser.find_element_by_tag_name('p').text
        self.assertEqual(list_text, 'There are no authors available.')

    def test_author_page_filled(self):
        Author.objects.create(first_name='John', last_name='Smith')

        self.browser.get(self.live_server_url + '/catalog/authors')
        list = self.browser.find_element_by_id('author-list')
        rows = list.find_elements_by_tag_name('li')
        self.assertIn('Smith, John (None - )', [row.text for row in rows])

    def test_author_page_create(self):
        self.login(self.user)
        self.browser.get(self.live_server_url + '/author/create/')

        first_name = self.browser.find_element_by_css_selector('input[name=first_name]')
        last_name = self.browser.find_element_by_css_selector('input[name=last_name]')
        date_of_birth = self.browser.find_element_by_css_selector('input[name=date_of_birth]')

        submit = self.browser.find_element_by_css_selector('input[type=submit]')

        first_name.send_keys('James')
        last_name.send_keys('Brown')
        date_of_birth.send_keys('11/09/1980')
        submit.send_keys(Keys.ENTER)
        time.sleep(1)

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual(header_text, 'Author: Brown, James')

    def test_author_page_delete(self):
        Author.objects.create(first_name='John', last_name='Smith')

        author = Author.objects.get(first_name='John')

        self.login(self.user)

        self.browser.get(self.live_server_url + '/catalog/author/'+ str(author.id))

        delete_button = self.browser.find_element_by_link_text('Delete')
        delete_button.click()

        submit = self.browser.find_element_by_css_selector('input[type=submit]')
        submit.send_keys(Keys.ENTER)

        time.sleep(1)

        self.browser.get(self.live_server_url + '/catalog/authors')

        list_text = self.browser.find_element_by_tag_name('p').text
        self.assertEqual(list_text, 'There are no authors available.')
        
    def test_author_page_update(self):
        Author.objects.create(first_name='John', last_name='Smith')

        author = Author.objects.get(first_name='John')

        self.login(self.user)

        self.browser.get(self.live_server_url + '/catalog/author/'+ str(author.id))

        delete_button = self.browser.find_element_by_link_text('Update')
        delete_button.click()

        first_name = self.browser.find_element_by_css_selector('input[name=first_name]')
        first_name.clear()
        first_name.send_keys('James')

        submit = self.browser.find_element_by_css_selector('input[type=submit]')
        submit.send_keys(Keys.ENTER)

        time.sleep(1)

        self.browser.get(self.live_server_url + '/catalog/authors')

        time.sleep(10)

        list = self.browser.find_element_by_id('author-list')
        rows = list.find_elements_by_tag_name('li')
        self.assertIn('Smith, James (None - )', [row.text for row in rows])