## Basic Setup

- Goal: A books app that displays all available books and has an individual page for each
- Create the `books` app
    - `docker-compose exec web python manage.py startapp books`
    - Add `books.apps.BooksConfig` to `settings.py`

### Make new models, admin, urls, views, templates

- New `models.py`, then `makemigrations books`, `migrate`

    ```python
    # books/models.py
    from django.db import models

    class Book(models.Model):
      title = models.CharField(max_length=200)
      author = models.CharField(max_length=200)
      price = models.DecimalField(max_digits=6, decimal_places=2)

      def __str__(self):
        return self.title
    ```

- New `admin.py`, then create a new book object in admin

    ```python
    from django.contrib import admin
    from .models import Book

    admin.site.register(Book)
    ```

- Update `admin.py` to display book details

    ```python
    # books/admin.py
    from django.contrib import admin
    from .models import Book

    class BookAdmin(admin.ModelAdmin):
      list_display = ("title", "author", "price",)

    admin.site.register(Book)
    ```

- New `urls.py`

    ```python
    # bookstore_project/urls.py
    from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
        # Django admin
        path('admin/', admin.site.urls),

        # User management
        path('accounts/', include('allauth.urls')),

        # Local apps
        path('', include('pages.urls')),
        path('books/', include('books.urls')),
    ]
    ```

    ```python
    # books/urls.py
    from django.urls import path

    from .views import BookListView

    urlpatterns = [
        path('', BookListView.as_view(), name='book_list'),
    ]
    ```

- New `views.py`

    ```python
    # books/views.py
    from django.views.generic import ListView

    from .models import Book

    class BookListView(ListView):
      model = Book
      template_name = 'books/book_list.html'
    ```

- New `templates/books/book_list.html`

    ```html
    <!-- templates/books/book_list.html -->
    {% extends '_base.html' %}

    {% block title %}Books{% endblock title %}

    {% block content %}
      {% for book in object_list %}
        <div>
          <h2><a href="">{{ book.title }}</a></h2>
        </div>
      {% endfor %}
    {% endblock content %}
    ```

- Switch the Docker containers off and on again, and we're good to go!

### Make object_list [friendlier](https://docs.djangoproject.com/en/2.2/topics/class-based-views/generic-display/#making-friendly-template-contexts)

- Update `books/views.py` with `context_object_name`

    ```python
    # books/views.py
    from django.views.generic import ListView, DetailView
    from .models import Book

    class BookListView(ListView):
      model = Book
      context_object_name = 'book_list' # new
      template_name = 'books/book_list.html'
    ```

- Update `book_list.html` with new `book_list` name

    ```html
    <!-- templates/books/book_list.html -->
    {% extends '_base.html' %}

    {% block title %}Books{% endblock title %}

    {% block content %}
      {% for book in book_list %}
        <div>
          <h2><a href="">{{ book.title }}</a></h2>
        </div>
      {% endfor %}
    {% endblock content %}
    ```

## Individual Book Page

- For now we'll use the primary key of each book
- Updated `[urls.py](http://urls.py)` to use `[<int:pk>](https://docs.djangoproject.com/en/2.2/topics/db/models/#automatic-primary-key-fields)` for unique urls

    ```python
    # books/urls.py
    from django.urls import path

    from .views import BookListView, BookDetailView

    urlpatterns = [
        path('', BookListView.as_view(), name='book_list'),
        path('<int:pk>', BookDetailView.as_view(), name='book_detail'),
    ]
    ```

- Updated `views.py`

    ```python
    # books/views.py
    from django.views.generic import ListView, DetailView

    from .models import Book

    class BookListView(ListView):
      model = Book
      context_object_name = 'book_list'
      template_name = 'books/book_list.html'

    class BookDetailView(DetailView):
      model = Book
      template_name = 'books/book_detail.html'
    ```

- New `books/book_detail.html`

    ```html
    <!-- templates/books/book_detail.html -->
    {% extends '_base.html' %}

    {% block title %}{{ object.title }}{% endblock title %}

    {% block content %}
    <div>
      <h2><a href="">{{ object.title }}</a></h2>
      <p>Author: {{ object.author }}</p>
      <p>Price: {{ object.price }}</p>
    </div>
    {% endblock content %}
    ```

### Make object_name friendlier

- Updated `views.py`

    ```python
    # books/views.py
    ...
    class BookDetailView(DetailView):
      model = Book
      context_object_name = 'book'
      template_name = 'books/book_detail.html'
    ```

- Update `book_detail.html`

    ```html
    <!-- templates/books/book_detail.html -->
    {% extends '_base.html' %}

    {% block title %}{{ book.title }}{% endblock title %}

    {% block content %}
    <div>
      <h2><a href="">{{ book.title }}</a></h2>
      <p>Author: {{ book.author }}</p>
      <p>Price: {{ book.price }}</p>
    </div>
    {% endblock content %}
    ```

- Update `book_list.html` to point to individual pages

    ```html
    <!-- templates/books/book_list.html -->
    {% extends '_base.html' %}

    {% block title %}Books{% endblock title %}

    {% block content %}
      {% for book in book_list %}
        <div>
          <h2><a href="{% url 'book_detail' book.pk %}">{{ book.title }}</a></h2>
        </div>
      {% endfor %}
    {% endblock content %}
    ```

### Add get_absolute_url and reverse()

- Updated `books/models.py`

    ```python
    # books/models.py
    from django.db import models
    from django.urls import reverse

    class Book(models.Model):
      title = models.CharField(max_length=200)
      author = models.CharField(max_length=200)
      price = models.DecimalField(max_digits=6, decimal_places=2)

      def __str__(self):
        return self.title

      def get_absolute_url(self): # new
        return reverse('book_detail', args=[str(self.id)])
    ```

- Updated `book_list.html`

    ```html
    <!-- templates/books/book_list.html -->
    {% extends '_base.html' %}

    {% block title %}Books{% endblock title %}

    {% block content %}
      {% for book in book_list %}
        <div>
          <h2><a href="{{ book.get_absolute_url }}">{{ book.title }}</a></h2>
        </div>
      {% endfor %}
    {% endblock content %}
    ```

- Always use THIS approach for individual pages in a project

## Primary Keys vs IDs

- `id` is a model field set automatically by Django to auto-increment. This is also treated as the primary key `pk` of a model
- BUT it's possible to manually change what the primary key is for a model. It doesn't have to be `id`, but it could be something like `object_id`

### Slugs vs UUIDs

- `pk` is quick and easy, but NOT good for a real-world project
    - Security issues
    - Can cause issues with frontends
- Slug — can be added with [SlugField](https://docs.djangoproject.com/en/2.2/ref/models/fields/#slugfield) model field, good for setting custom urls for each individual item
- [UUID](https://docs.python.org/3/library/uuid.html?highlight=uuid#module-uuid)'s are supported with the [UUIDField](https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.UUIDField). This is a better approach!
- Updated `models.py`

    ```python
    # books/models.py
    import uuid
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

      def __str__(self):
        return self.title

      def get_absolute_url(self):
        return reverse('book_detail', args=[str(self.id)])
    ```

- Updated `urls.py`

    ```python
    # books/urls.py
    from django.urls import path

    from .views import BookListView, BookDetailView

    urlpatterns = [
        path('', BookListView.as_view(), name='book_list'),
        path('<uuid:pk>', BookDetailView.as_view(), name='book_detail'),
    ]
    ```

- Delete `books/migrations`...a destructive approach that works for this instance
    - Then take down Docker
- Delete the PostgreSQL volume and start over with Docker...more mature projects can't do this, but we caaaan!
- Fix Docker
    - `docker volume rm books_postgres_data`
    - `docker-compose up -d`
    - `docker-compose exec web python manage.py makemigrations books`
    - `docker-compose exec web python manage.py migrate`
    - `docker-compose exec web python manage.py createsuperuser`
- Go to admin and add three books again

## Add Books to Navbar

- Updated `_base.html`

    ```html
    <!-- templates/_base.html -->
    <nav class="my-2 my-md-0 mr-md-3">
      <a class="p-2 text-dark" href="{% url 'book_list' %}">Books</a>
    ```

## Add tests

- Updated `books/tests.py`

    ```python
    # books/tests.py
    from django.test import TestCase
    from django.urls import reverse
    from .models import Book

    class BookTests(TestCase):
        def setUp(self):
            self.book = Book.objects.create(
                title='Harry Potter',
                author='JK Rowling',
                price='25.00',
            )

        def test_book_listing(self):
            self.assertEqual(f'{self.book.title}', 'Harry Potter')
            self.assertEqual(f'{self.book.author}', 'JK Rowling')
            self.assertEqual(f'{self.book.price}', '25.00')

        def test_book_list_view(self):
            response = self.client.get(reverse('book_list'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Harry Potter')
            self.assertTemplateUsed(response, 'books/book_list.html')

        def test_book_detail_view(self):
            response = self.client.get(self.book.get_absolute_url())
            no_response = self.client.get('/books/12345/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(no_response.status_code, 404)
            self.assertContains(response, 'Harry Potter')
            self.assertTemplateUsed(response, 'books/book_detail.html')
    ```

- Run tests: `docker-compose exec web python manage.py test`