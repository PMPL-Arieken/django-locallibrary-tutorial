import time
from .base import FunctionalTest
from catalog.models import Author
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User
class TestAuthorPage(FunctionalTest):

    def setUp(self):
        return super().setUp()

    def tearDown(self):
        return super().tearDown()

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
        self.login(self.admin)
        self.browser.get(self.live_server_url + '/author/create/')

        time.sleep(1)

        first_name = self.browser.find_element_by_css_selector('input[name=first_name]')
        last_name = self.browser.find_element_by_css_selector('input[name=last_name]')
        date_of_birth = self.browser.find_element_by_css_selector('input[name=date_of_birth]')

        time.sleep(1)

        submit = self.browser.find_element_by_css_selector('input[type=submit]')

        first_name.send_keys('James')
        last_name.send_keys('Brown')
        date_of_birth.send_keys('11/09/1980')
        submit.send_keys(Keys.ENTER)
        time.sleep(1)

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual(header_text, 'Author: Brown, James')

    def test_author_page_delete(self):
        self.setUpBooks()

        self.login(self.admin)

        self.browser.get(self.live_server_url + '/catalog/author/'+ str(self.author.id))

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

        self.login(self.admin)

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
        list = self.browser.find_element_by_id('author-list')
        rows = list.find_elements_by_tag_name('li')
        self.assertIn('Smith, James (None - )', [row.text for row in rows])