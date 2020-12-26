from django.shortcuts import redirect
from django.test import TestCase

# Create your tests here.
from catalog.models import Book, Author, BookInstance, Genre
from catalog.views import index

password1 = '1X<ISRUkw+tuK'
password2 = '2HJ1vRV0Z&3iD'
book_title = 'Book Title'
book_summary = 'My book summary'
imprint = 'Unlikely Imprint, 2016'
permission_name = 'Set book as returned'


class IndexViewTest(TestCase):
    def test_counts_for_numbooks_numinstances_and_numauthors_on_index(self):
        login = self.client.login(username='user', password='letkenp4ss')
        response = self.client.get('/catalog/')

        num_books = Book.objects.all().count()
        num_instances = BookInstance.objects.all().count()
        num_instances_available = BookInstance.objects.filter(
            status__exact='a').count()
        num_authors = Author.objects.count()

        self.assertEqual(num_books, Book.objects.all().count())
        self.assertEqual(num_instances, BookInstance.objects.all().count())
        self.assertEqual(
            num_instances_available,
            BookInstance.objects.filter(status__exact='a').count())
        self.assertEqual(num_authors, Author.objects.count())


from django.urls import reverse


class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create authors for pagination tests
        number_of_authors = 13
        for author_id in range(number_of_authors):
            Author.objects.create(first_name='Christian {0}'.format(author_id),
                                  last_name='Surname {0}'.format(author_id))

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue(len(response.context['author_list']) == 10)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) the remaining 3 items
        response = self.client.get(reverse('authors') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue(len(response.context['author_list']) == 3)


import datetime
from django.utils import timezone

from catalog.models import BookInstance, Book, Genre, Language
from django.contrib.auth.models import User  # Required to assign User as a borrower


class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password=password1)
        test_user2 = User.objects.create_user(username='testuser2',
                                              password=password2)

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John',
                                            last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title=book_title,
            summary=book_summary,
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )
        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy %
                                                              5)
            if book_copy % 2:
                the_borrower = test_user1
            else:
                the_borrower = test_user2
            status = 'm'

            BookInstance.objects.create(book=test_book,
                                        imprint=imprint,
                                        due_back=return_date,
                                        borrower=the_borrower,
                                        status=status)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response,
                             '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password=password1)
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(
            response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password=password1)
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change all books to be on loan
        get_ten_books = BookInstance.objects.all()[:10]

        for copy in get_ten_books:
            copy.status = 'o'
            copy.save()

        # Check that now we have borrowed books in the list
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        # Confirm all books belong to testuser1 and are on loan
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_paginated_to_ten(self):

        # Change all books to be on loan.
        # This should make 15 test user ones.
        for copy in BookInstance.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.login(username='testuser1', password=password1)
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that only 10 items are displayed due to pagination
        # (if pagination not enabled, there would be 15 returned)
        self.assertEqual(len(response.context['bookinstance_list']), 10)

    def test_pages_ordered_by_due_date(self):

        # Change all books to be on loan
        for copy in BookInstance.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.login(username='testuser1', password=password1)
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(response.context['bookinstance_list']), 10)

        last_date = 0
        for copy in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)


from django.contrib.auth.models import Permission  # Required to grant the permission needed to set a book as returned.


class TestCaseWithFixtures(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1',
                                              password=password1)
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2',
                                              password=password2)
        test_user2.save()
        permission = Permission.objects.get(name=permission_name)
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John',
                                            last_name='Smith')
        self.test_genre = Genre.objects.create(name='Fantasy')
        self.test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title=book_title,
            summary=book_summary,
            isbn='ABCDEFG',
            author=test_author,
            language=self.test_language,
        )
        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint=imprint,
            due_back=return_date,
            borrower=test_user1,
            status='o')

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint=imprint,
            due_back=return_date,
            borrower=test_user2,
            status='o')


class RenewBookInstancesViewTest(TestCaseWithFixtures):
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password=password1)
        response = self.client.get(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password=password2)
        response = self.client.get(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance2.pk}))

        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password=password2)
        response = self.client.get(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}))

        # Check that it lets us login. We're a librarian, so we can view any users book
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password=password2)
        response = self.client.get(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password=password2)
        response = self.client.get(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(
            weeks=3)
        self.assertEqual(response.context['form'].initial['renewal_date'],
                         date_3_weeks_in_future)

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password=password2)

        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.post(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}),
            {'renewal_date': date_in_past})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date',
                             'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password=password2)

        invalid_date_in_future = datetime.date.today() + datetime.timedelta(
            weeks=5)
        response = self.client.post(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}),
            {'renewal_date': invalid_date_in_future})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date',
                             'Invalid date - renewal more than 4 weeks ahead')

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password=password2)
        valid_date_in_future = datetime.date.today() + datetime.timedelta(
            weeks=2)
        response = self.client.post(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}),
            {'renewal_date': valid_date_in_future})
        self.assertRedirects(response, reverse('all-borrowed'))

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        import uuid
        test_uid = uuid.uuid4()  # unlikely UID to match our bookinstance!
        login = self.client.login(username='testuser2', password=password2)
        response = self.client.get(
            reverse('renew-book-librarian', kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code, 404)


class AuthorCreateViewTest(TestCase):
    """Test case for the AuthorCreate view (Created as Challenge)."""
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1',
                                              password=password1)
        test_user2 = User.objects.create_user(username='testuser2',
                                              password=password2)

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name=permission_name)
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John',
                                            last_name='Smith')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author_create'))
        self.assertRedirects(response,
                             '/accounts/login/?next=/catalog/author/create/')

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password=password1)
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password=password2)
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password=password2)
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

    def test_form_date_of_death_initially_set_to_expected_date(self):
        login = self.client.login(username='testuser2', password=password2)
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 200)

        expected_initial_date = datetime.date(2020, 6, 11)
        response_date = response.context['form'].initial['date_of_death']
        response_date = datetime.datetime.strptime(response_date,
                                                   "%d/%m/%Y").date()
        self.assertEqual(response_date, expected_initial_date)

    def test_redirects_to_detail_view_on_success(self):
        login = self.client.login(username='testuser2', password=password2)
        response = self.client.post(reverse('author_create'), {
            'first_name': 'Christian Name',
            'last_name': 'Surname'
        })
        # Manually check redirect because we don't know what author was created
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/catalog/author/'))


class BorrowBookViewTest(TestCase):
    def setUp(self):
        # Create two users
        self.test_user1 = User.objects.create_user(username='testuser1',
                                                   password=password1)
        self.test_user2 = User.objects.create_user(username='testuser2',
                                                   password=password2)

        self.test_user1.save()
        self.test_user2.save()

        # Create a book
        self.test_author = Author.objects.create(first_name='John',
                                                 last_name='Smith')
        self.test_genre = Genre.objects.create(name='Fantasy')
        self.test_language = Language.objects.create(name='English')
        self.test_book = Book.objects.create(
            title=book_title,
            summary=book_summary,
            isbn='ABCDEFG',
            author=self.test_author,
            language=self.test_language,
        )
        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        self.test_book.genre.set(genre_objects_for_book)
        self.test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 5
        for book_copy in range(number_of_book_copies):
            status = 'a'
            book_copy = BookInstance.objects.create(book=self.test_book,
                                                    imprint=imprint,
                                                    status=status)
            book_copy.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('borrow', args=[self.test_book.id]))
        self.assertRedirects(
            response,
            f'/accounts/login/?next=/catalog/borrow/{self.test_book.id}')

    def test_book_page_borrow_available(self):
        self.client.login(username='testuser1', password=password1)
        response = self.client.get(self.test_book.get_absolute_url())
        self.assertContains(
            response,
            f'<a href="/catalog/borrow/{self.test_book.id}">Borrow</a>')

    def test_book_page_borrow_notavailable(self):
        for inst in self.test_book.bookinstance_set.all():
            inst.status = 'm'
            inst.save()

        self.client.login(username='testuser1', password=password1)
        response = self.client.get(self.test_book.get_absolute_url())
        self.assertContains(response, 'Book not available')

    def test_borrow_page_book_available(self):
        self.client.login(username='testuser1', password=password1)
        response = self.client.get(reverse('borrow', args=[self.test_book.id]))
        self.assertContains(response, self.test_book.available_instance)

    def test_borrow_page_book_notavailable(self):
        for inst in self.test_book.bookinstance_set.all():
            inst.status = 'm'
            inst.save()

        self.client.login(username='testuser1', password=password1)
        response = self.client.get(reverse('borrow', args=[self.test_book.id]))
        self.assertContains(response, 'Book not available')

    def test_borrow_available_book(self):
        self.client.login(username='testuser1', password=password1)

        inst = self.test_book.available_instance
        response = self.client.post(
            reverse('borrow', args=[self.test_book.id]), {'instance': inst})

        self.assertRedirects(response, f'/catalog/borrow/{inst}/success')

    def test_borrow_nonavailable_book(self):
        self.client.login(username='testuser1', password=password1)
        inst = self.test_book.available_instance

        for i in self.test_book.bookinstance_set.all():
            i.status = 'm'
            i.save()

        response = self.client.post(
            reverse('borrow', args=[self.test_book.id]), {'instance': inst})

        self.assertRedirects(response, f'/catalog/borrow/{inst}/fail')


class ReturnBookInstancesViewTest(TestCaseWithFixtures):
    def test_page_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse('return-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}))

        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password=password1)
        response = self.client.get(
            reverse('return-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password=password2)
        response = self.client.get(
            reverse('return-book-librarian',
                    kwargs={'pk': self.test_bookinstance2.pk}))

        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password=password2)
        response = self.client.get(
            reverse('return-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}))

        # Check that it lets us login. We're a librarian, so we can view any users book
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password=password2)
        response = self.client.get(
            reverse('return-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/book_return_librarian.html')

    def test_return_with_invalid_date(self):
        login = self.client.login(username='testuser2', password=password2)

        response = self.client.post(
            reverse('return-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}), {
                        'return_date':
                        datetime.date.today() + datetime.timedelta(days=1),
                        'penalty': 0
                    })
        self.assertContains(response, 'Invalid date - return in future')
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'return_date',
                             'Invalid date - return in future')

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password=password2)

        response = self.client.post(
            reverse('return-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}), {
                        'return_date': datetime.date.today(),
                        'penalty': 0
                    })
        self.assertRedirects(response, reverse('all-borrowed'))

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        import uuid
        test_uid = uuid.uuid4()  # unlikely UID to match our bookinstance!
        login = self.client.login(username='testuser2', password=password2)
        response = self.client.get(
            reverse('return-book-librarian', kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code, 404)


class BookMaintainViewTest(TestCaseWithFixtures):
    def test_create_button_for_unauthenticated_users(self):
        response = self.client.get(reverse('books'))
        self.assertNotContains(response, 'Create new Book')

    def test_create_button_for_authenticated_users(self):
        self.client.login(username='testuser1', password=password1)
        response = self.client.get(reverse('books'))
        self.assertContains(response, 'Create new Book')

    def test_update_delete_button_for_unauthenticated_users(self):
        response = self.client.get(reverse('book-detail', args=[1]))
        self.assertNotContains(response, 'Update')
        self.assertNotContains(response, 'Delete')

    def test_update_delete_button_for_authenticated_users(self):
        self.client.login(username='testuser1', password=password1)
        response = self.client.get(reverse('book-detail', args=[1]))
        self.assertContains(response, 'Update')
        self.assertContains(response, 'Delete')


import urllib.parse


class LanguageMaintainTest(TestCaseWithFixtures):
    
    def test_page_language_list_authorized(self):
        self.client.login(username='testuser2', password=password2)
        response = self.client.get(reverse('languages'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Language")

    def test_page_language_update_authorized(self):
        self.client.login(username='testuser2', password=password2)
        response = self.client.get(
            reverse('languages') + f'?update={self.test_language.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Update Language")

    def test_page_language_unauthorized(self):
        urls = [
            reverse('languages'),
            reverse('languages') + f'?delete={self.test_language.id}',
            reverse('languages') + f'?update={self.test_language.id}'
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            redirect_url = reverse(
                'login') + f'?next={urllib.parse.quote(url)}'
            self.assertEqual(response.url, redirect_url)

    def test_create_language(self):
        self.client.login(username='testuser2', password=password2)
        self.client.post(reverse('language_create'), {'language':'New Language'})
        self.assertEqual(Language.objects.filter(name='New Language').count(), 1)

    def test_update_language(self):
        self.client.login(username='testuser2', password=password2)
        self.client.post(reverse('language_update'), {'id':self.test_language.id, 'language':'New Language'})
        self.test_language.refresh_from_db()
        self.assertEqual(self.test_language.name, 'New Language')


    def test_delete_language_with_books(self):
        self.client.login(username='testuser2', password=password2)
        response = self.client.get(
            reverse('languages') + f'?delete={self.test_language.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Language.objects.filter(id=self.test_language.id).count(), 1)

    def test_delete_language_without_books(self):
        self.client.login(username='testuser2', password=password2)
        
        new_lang = Language(name="New Lang")
        new_lang.save()
        
        response = self.client.get(
            reverse('languages') + f'?delete={new_lang.id}')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Language.objects.filter(id=new_lang.id).count(), 0)
class GenreMaintainTest(TestCaseWithFixtures):

    def test_page_genre_list_authorized(self):
        self.client.login(username='testuser2', password=password2)
        response = self.client.get(reverse('genres'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Genre")

    def test_page_genre_update_authorized(self):
        self.client.login(username='testuser2', password=password2)
        response = self.client.get(
            reverse('genres') + f'?update={self.test_genre.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Update Genre")

    def test_page_genre_unauthorized(self):
        urls = [
            reverse('genres'),
            reverse('genres') + f'?delete={self.test_genre.id}',
            reverse('genres') + f'?update={self.test_genre.id}'
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            redirect_url = reverse(
                'login') + f'?next={urllib.parse.quote(url)}'
            self.assertEqual(response.url, redirect_url)

    def test_create_genre(self):
        self.client.login(username='testuser2', password=password2)
        self.client.post(reverse('genre_create'), {'genre':'New Genre'})
        self.assertEqual(Genre.objects.filter(name='New Genre').count(), 1)

    def test_update_genre(self):
        self.client.login(username='testuser2', password=password2)
        self.client.post(reverse('genre_update'), {'id':self.test_genre.id, 'genre':'New Genre'})
        self.test_genre.refresh_from_db()
        self.assertEqual(self.test_genre.name, 'New Genre')


    def test_delete_genre_with_books(self):
        self.client.login(username='testuser2', password=password2)
        response = self.client.get(
            reverse('genres') + f'?delete={self.test_genre.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Genre.objects.filter(id=self.test_genre.id).count(), 1)

    def test_delete_genre_without_books(self):
        self.client.login(username='testuser2', password=password2)

        new_genre = Genre(name="New Genre")
        new_genre.save()

        response = self.client.get(
            reverse('genres') + f'?delete={new_genre.id}')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Genre.objects.filter(id=new_genre.id).count(), 0)