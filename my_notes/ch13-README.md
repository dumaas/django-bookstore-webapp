## Logged-In Users Only

- Django's [built-in authorization options](https://docs.djangoproject.com/en/2.2/topics/auth/default/#permissions-and-authorization) make this easy!
- The easiest way to do this is with the [LoginRequired mixin](https://docs.djangoproject.com/en/2.2/topics/auth/default/#the-login-required-decorator)
- Updated `views.py`

    ```python
    # books/views.py
    from django.contrib.auth.mixins import LoginRequiredMixin
    from django.views.generic import ListView, DetailView

    from .models import Book

    class BookListView(LoginRequiredMixin, ListView):
      model = Book
      context_object_name = 'book_list'
      template_name = 'books/book_list.html'
      login_url = 'account_login'

    class BookDetailView(LoginRequiredMixin, DetailView):
      model = Book
      context_object_name = 'book'
      template_name = 'books/book_detail.html'
      login_url = 'account_login'
    ```

- Easy-peasy!

## Permissions

- Django's basic [permissions system](https://docs.djangoproject.com/en/2.2/topics/auth/default/#permissions-and-authorization) is controlled in the admin.
- Cretae a new user `special` with email `special@email.com`

### [Custom Permissions](https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#custom-permissions)

- Set permissions for an author to read all book
- Updated `models.py`

    ```python
    # books/models.py
    import uuid
    from django.contrib.auth import get_user_model
    from django.db import models
    from django.urls import reverse

    class Book(models.Model):
      id = models.UUIDField(
          primary_key=True,
          default=uuid.uuid4,
          editable=False)
      title = models.CharField(max_length=200)
      author = models.CharField(max_length=200)
      price = models.DecimalField(max_digits=6, decimal_places=2)
      cover = models.ImageField(upload_to='covers/', blank=True)

      class Meta:
        permissions = [
            ('special_status', 'Can read all books'),
        ]

      def __str__(self):
        return self.title

      def get_absolute_url(self):
        return reverse('book_detail', args=[str(self.id)])
    ```

- Makemigrations, then migrate

### User Permissions

- Apply the new custom permission to the `special` user from within the admin
    - Add `books | book | Can read all books` permission

### [PermissionRequiredMixin](https://docs.djangoproject.com/en/2.2/topics/auth/default/#the-permissionrequiredmixin-mixin)

- Use this to apply the custom permission
- Updated `views.py`

    ```python
    # books/views.py
    from django.contrib.auth.mixins import (
        LoginRequiredMixin,
        PermissionRequiredMixin
    )
    from django.views.generic import ListView, DetailView

    from .models import Book

    class BookListView(LoginRequiredMixin, ListView):
      model = Book
      context_object_name = 'book_list'
      template_name = 'books/book_list.html'
      login_url = 'account_login'

    class BookDetailView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        DetailView
    ):
      model = Book
      context_object_name = 'book'
      template_name = 'books/book_detail.html'
      login_url = 'account_login'
      permission_required = 'books.special_status'
    ```

- Note: it's possible to add [multiple permissions](https://docs.djangoproject.com/en/2.2/topics/auth/default/#the-permissionrequiredmixin-mixin) with the `permission_required` field
- Test this with the testuser account, and see that clicking on any of the individual book pages redirects to `403 Forbidden`
- With the special account, navigating to these individual pages works perfectly!

### [Groups](https://docs.djangoproject.com/en/2.2/topics/auth/default/#groups) & [UserPassesTestMixin](https://docs.djangoproject.com/en/2.2/topics/auth/default/#django.contrib.auth.mixins.UserPassesTestMixin)

- Groups are great at scale, since you can automate the changing of user groups within the code logic

## Tests

- Run tests, notice that they fail!!! o.o
    - This is because of the requirement for being logged in to view the list of books and the `special_status` permission for viewing book detail pages
- Updated `tests.py`

    ```python
    # books/tests.py
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Permission
    from django.test import TestCase
    from django.urls import reverse
    from .models import Book, Review

    class BookTests(TestCase):

        def setUp(self):
            self.user = get_user_model().objects.create_user(
                username='reviewuser',
                email='reviewuser@email.com',
                password='testpass123'
            )
            self.special_permission = Permission.objects.get(
                codename='special_status')
            self.book = Book.objects.create(
                title='Harry Potter',
                author='JK Rowling',
                price='25.00',
            )
            self.review = Review.objects.create(
                book = self.book,
                author = self.user,
                review = 'An excellent review',
            )

        def test_book_listing(self):
            self.assertEqual(f'{self.book.title}', 'Harry Potter')
            self.assertEqual(f'{self.book.author}', 'JK Rowling')
            self.assertEqual(f'{self.book.price}', '25.00')

        def test_book_list_view_for_logged_in_user(self):
            self.client.login(email='reviewuser@email.com', password='testpass123')
            response = self.client.get(reverse('book_list'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Harry Potter')
            self.assertTemplateUsed(response, 'books/book_list.html')

        def test_book_list_view_for_logged_out_user(self):
            self.client.logout()
            response = self.client.get(reverse('book_list'))
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(
                response, '%s?next=/books/' % (reverse('account_login')))
            response = self.client.get(
                '%s?next=/books/' % (reverse('account_login')))
            self.assertContains(response, 'Log In')

        def test_book_detail_view_with_permissions(self):
            self.client.login(email='reviewuser@email.com', password='testpass123')
            self.user.user_permissions.add(self.special_permission)
            response = self.client.get(self.book.get_absolute_url())
            no_response = self.client.get('/books/12345/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(no_response.status_code, 404)
            self.assertContains(response, 'Harry Potter')
            self.assertContains(response, 'An excellent review')
            self.assertTemplateUsed(response, 'books/book_detail.html')
    ```