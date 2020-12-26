from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('borrow/<int:pk>', views.BorrowBookView.as_view(), name='borrow'),
    path('borrow/<str:pk>/success', views.BorrowBookSuccessView.as_view(), name='borrow_success'),
    path('borrow/<str:pk>/fail', views.BorrowBookFailView.as_view(), name='borrow_fail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>',
         views.AuthorDetailView.as_view(), name='author-detail'),
]


urlpatterns += [
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path(r'borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),  # Added for challenge
]


# Add URLConf for librarian to renew a book.
urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
    path('book/<uuid:pk>/return/', views.return_book_librarian, name='return-book-librarian'),
]


# Add URLConf to create, update, and delete authors
urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author_create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author_update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author_delete'),
]

# Add URLConf to create, update, and delete books
urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book_create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book_update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book_delete'),
]

# Add URLConf to create, update, and delete Language
urlpatterns += [
    path('languages/', views.LanguageListView.as_view(), name='languages'),
    path('language/create/', views.LanguageCreate.as_view(), name='language_create'),
    path('language/update/', views.LanguageUpdate.as_view(), name='language_update'),
]

urlpatterns += [
    path('genres/', views.GenreListView.as_view(), name='genres'),
    path('genre/create/', views.GenreCreate.as_view(), name='genre_create'),
    path('genre/update/', views.GenreUpdate.as_view(), name='genre_update'),
]