from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from catalog.models import Author, Book, BookInstance, Genre, Language
from django.contrib.auth.models import User
import sys
from selenium import webdriver

class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def userSetup(self):
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
        Genre.objects.create(name='Fantasy')
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

    def tearDown(self):
        self.browser.quit()

