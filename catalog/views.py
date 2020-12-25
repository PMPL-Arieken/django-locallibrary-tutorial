from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

# Create your views here.

from .models import Book, Author, BookInstance, Genre
import datetime

permission_name = 'catalog.can_mark_returned'


def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available copies of books
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()
    num_authors = Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
        context={
            'num_books': num_books,
            'num_instances': num_instances,
            'num_instances_available': num_instances_available,
            'num_authors': num_authors,
            'num_visits': num_visits
        },
    )


from django.views import generic


class BookListView(generic.ListView):
    """Generic class-based view for a list of books."""
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    model = Book


class AuthorListView(generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""
    model = Author


class BorrowBookView(generic.DetailView):
    template_name = 'catalog/borrowbook.html'
    model = Book
    due_back = datetime.date.today() + datetime.timedelta(weeks=2)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['due_back'] = self.due_back
        return context

    def post(self, request, *args, **kwargs):
        instance_id = request.POST.get('instance')
        book_instance = BookInstance.objects.get(id=instance_id)
        if book_instance.status == 'a':
            book_instance.due_back = self.due_back
            book_instance.borrower = request.user
            book_instance.status = 'o'
            book_instance.save()
            return redirect(
                reverse('borrow_success', args=[str(book_instance.id)]))
        else:
            return redirect(
                reverse('borrow_fail', args=[str(book_instance.id)]))


class BorrowBookSuccessView(generic.DetailView):
    template_name = 'catalog/borrowbook_success.html'
    context_object_name = 'book_instance'
    model = BookInstance


class BorrowBookFailView(generic.DetailView):
    template_name = 'catalog/borrowbook_fail.html'
    context_object_name = 'book_instance'
    model = BookInstance


from django.contrib.auth.mixins import LoginRequiredMixin


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(
            status__exact='o').order_by('due_back')


# Added as part of challenge!
from django.contrib.auth.mixins import PermissionRequiredMixin


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = permission_name
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(
            status__exact='o').order_by('due_back')


from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from catalog.forms import RenewBookForm, ReturnBookForm


@login_required
@permission_required(permission_name, raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(
            weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


@login_required
@permission_required(permission_name, raise_exception=True)
def return_book_librarian(request, pk):
    """View function for returning a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = ReturnBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.status = 'a'
            book_instance.borrower = None
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        form = ReturnBookForm(initial={'return_date': datetime.date.today()})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_return_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author, Language
from django.core.exceptions import ValidationError


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    permission_required = permission_name


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__'  # Not recommended (potential security issue if more fields added)
    permission_required = permission_name


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = permission_name


# Classes created for the forms challenge
class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = permission_name


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = permission_name


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = permission_name


class LanguageListView(PermissionRequiredMixin, generic.ListView):

    permission_required = permission_name
    model = Language
    error = None
    update = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['error'] = self.error
        context['update'] = self.update
        return context

    def get(self, request, *args, **kwargs):            
        try:
            lang = request.GET.get('delete')
            if lang is not None:
                return self.get_delete(lang, request, *args, **kwargs)

            lang = request.GET.get('update')            
            if lang is not None:
                return self.get_update(lang, request, *args, **kwargs)

        except ValidationError as e:
            self.error = e.message

        return super().get(self, request, *args, **kwargs)

    def get_delete(self, lang, request, *args, **kwargs):
        if Language.objects.get(id=lang).book_set.count() > 0:
            raise ValidationError('Some books are still using this language!')
        else:
            Language.objects.get(id=lang).delete()
            return redirect(reverse('languages'))

    def get_update(self, lang, request, *args, **kwargs):
        self.update = Language.objects.get(id=lang)
        return super().get(self, request, *args, **kwargs)

class LanguageCreate(PermissionRequiredMixin, generic.View):
    permission_required = permission_name

    def post(self, request, *args, **kwargs):
        lang = request.POST.get('language')
        Language(name=lang).save()
        return redirect(reverse('languages'))

class LanguageUpdate(PermissionRequiredMixin, generic.View):
    permission_required = permission_name

    def post(self, request, *args, **kwargs):
        lang = request.POST.get('id')
        name = request.POST.get('language')
        
        lang_obj = Language.objects.get(id=lang)
        lang_obj.name = name
        lang_obj.save()
        return redirect(reverse('languages'))

        
