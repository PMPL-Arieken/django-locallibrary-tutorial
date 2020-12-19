import datetime
import time
from .base import FunctionalTest
from django.utils import timezone
from catalog.models import Author, Book, BookInstance, Genre, Language
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from django.contrib.auth.models import User

bookCatalogLink = '/catalog/books/'
bookDetailsLink = '/catalog/book/'

class TestBookPage(FunctionalTest):

    def setUp(self):
        super().setUp()

        password = '1X<ISRUkw+tuK'

        self.admin = {
            'username': 'admin', 
            'password': password,
            'is_staff': True,
            'is_active' : True,
            'is_superuser' : True,
        }

        self.user = {
            'username': 'testuser', 
            'password': password,
        }

        User.objects.create_user(**self.admin).save()
        User.objects.create_user(**self.user).save()

    def setUpBooks(self):
        # Create two users
        password = '1X<ISRUkw+tuK'
        test_user1 = User.objects.create_user(username='testuser1', password=password)
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language
        )
        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy % 5)
            if book_copy % 2:
                the_borrower = test_user1
            else:
                the_borrower = test_user2
            status = 'o'
            BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', due_back=return_date,
                                        borrower=the_borrower, status=status)

    def login(self, user):
        self.browser.get(self.live_server_url + "/accounts/login/")
        username = self.browser.find_element_by_css_selector('input[name=username]')
        password = self.browser.find_element_by_css_selector('input[name=password]')
        submit = self.browser.find_element_by_css_selector('input[type=submit]')

        username.send_keys(user['username'])
        password.send_keys(user['password'])

        submit.send_keys(Keys.ENTER)
        time.sleep(1)

    def test_book_page_empty(self):
        self.browser.get(self.live_server_url + bookCatalogLink)
        self.assertEqual(self.browser.title, 'Local Library')
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual(header_text, 'Book List')
        list_text = self.browser.find_element_by_tag_name('p').text
        self.assertEqual(list_text, 'There are no books in the library.')

    def test_book_page_filled(self):
        self.setUpBooks()
        self.browser.get(self.live_server_url + bookCatalogLink)
        time.sleep(10)
        list = self.browser.find_element_by_id('book-list')
        rows = list.find_elements_by_tag_name('li')
        self.assertIn('Book Title (Smith, John)', [row.text for row in rows])

    def test_book_page_create(self):
        self.setUpBooks()
        self.login(self.admin)
        self.browser.get(self.live_server_url + '/book/create/')

        time.sleep(10)

        title = self.browser.find_element_by_css_selector('input[name=title]')
        author_box = Select(self.browser.find_element_by_name('author'))
        summary = self.browser.find_element_by_css_selector('textarea[name=summary]')
        isbn = self.browser.find_element_by_css_selector('input[name=isbn]')
        genre_box = Select(self.browser.find_element_by_name('genre'))
        language = Select(self.browser.find_element_by_name('language'))
        submit = self.browser.find_element_by_css_selector('input[type=submit]')

        title.send_keys('Book Title 2')
        author_box.select_by_visible_text('Smith, John')
        summary.send_keys('Summary of Book 2')
        isbn.send_keys('1234567890123')
        genre_box.select_by_visible_text('Fantasy')
        language.select_by_visible_text('English')
        submit.send_keys(Keys.ENTER)
        time.sleep(1)

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual(header_text, 'Title: Book Title 2')

    def test_book_page_delete(self):
        self.setUpBooks()
        book = Book.objects.get(title='Book Title')

        self.login(self.admin)
        self.browser.get(self.live_server_url + bookDetailsLink + str(book.id))
        delete_button = self.browser.find_element_by_link_text('Delete')
        delete_button.click()

        submit = self.browser.find_element_by_css_selector('input[type=submit]')
        submit.send_keys(Keys.ENTER)

        time.sleep(1)

        self.browser.get(self.live_server_url + bookCatalogLink)

        list_text = self.browser.find_element_by_tag_name('p').text
        self.assertEqual(list_text, 'There are no books in the library.')
        
    def test_book_page_update(self):
        self.setUpBooks()
        book = Book.objects.get(title='Book Title')

        self.login(self.admin)

        self.browser.get(self.live_server_url + bookDetailsLink + str(book.id))

        delete_button = self.browser.find_element_by_link_text('Update')
        delete_button.click()

        time.sleep(1)

        title = self.browser.find_element_by_css_selector('input[name=title]')
        title.clear()
        title.send_keys('Laskar')

        submit = self.browser.find_element_by_css_selector('input[type=submit]')
        submit.send_keys(Keys.ENTER)

        time.sleep(1)

        self.browser.get(self.live_server_url + bookCatalogLink)
        list = self.browser.find_element_by_id('book-list')
        rows = list.find_elements_by_tag_name('li')
        self.assertIn('Laskar (Smith, John)', [row.text for row in rows])