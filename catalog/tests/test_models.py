import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

# Create your tests here.

from catalog.models import Author, Book, BookInstance, Genre, Language


class AuthorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'first name')

    def test_last_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('last_name').verbose_name
        self.assertEquals(field_label, 'last name')

    def test_date_of_birth_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEquals(field_label, 'date of birth')

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEquals(field_label, 'died')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 100)

    def test_last_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('last_name').max_length
        self.assertEquals(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = '{0}, {1}'.format(author.last_name, author.first_name)

        self.assertEquals(expected_object_name, str(author))

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEquals(author.get_absolute_url(), '/catalog/author/1')

class GeneralModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Create data for each model
        """
        cls.genre1 = Genre.objects.create(name='Computer Science')
        cls.genre2 = Genre.objects.create(name='Programming')
        cls.language = Language.objects.create(name='English')
        cls.author = Author.objects.create(first_name='John', last_name='Smith')
        cls.book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=cls.author,
            language=cls.language,
        )
        cls.book.genre.set((cls.genre1, cls.genre2))

        cls.user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        cls.user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        return_date = timezone.now() + datetime.timedelta(days=5)
        return_date_minus = timezone.now() + datetime.timedelta(days=-1)

        cls.book_instance1 = BookInstance.objects.create(
                                book=cls.book, 
                                imprint='Unlikely Imprint, 2016', 
                                due_back=return_date_minus.date(),
                                borrower=cls.user1, status='m')
        cls.book_instance2 = BookInstance.objects.create(
                                book=cls.book, 
                                imprint='Unlikely Imprint, 2016', 
                                due_back=return_date.date(),
                                borrower=cls.user2, status='m')


    def test_genre_properties(self):
        self.assertEqual(str(GeneralModelTest.genre1), 'Computer Science')
        self.assertEqual(str(GeneralModelTest.genre2), 'Programming')

    def test_language_properties(self):
        self.assertEqual(str(GeneralModelTest.language), 'English')

    def test_book_properties(self):
        self.assertEqual(GeneralModelTest.book.display_genre(), 'Computer Science, Programming')
        self.assertEqual(GeneralModelTest.book.get_absolute_url(), '/catalog/book/1')
        self.assertEqual(str(GeneralModelTest.book), 'Book Title')

    def test_book_instance_properties(self):
        self.assertTrue(GeneralModelTest.book_instance1.is_overdue)
        self.assertEqual(str(GeneralModelTest.book_instance1), f'{GeneralModelTest.book_instance1.id} (Book Title)')



