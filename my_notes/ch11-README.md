## Foreign Keys

- Each user needs a primary key field that's unique. This is important when we're linking two tables together!
- Since we're going to link the `Books` model with the `Reviews` model, this implies a foreign key relationship
- Types of foreign key relationships...
    - [One to one](https://docs.djangoproject.com/en/2.2/ref/models/fields/#onetoonefield) example — in a table of people's names and SSN's, each person has only one SSN, and each SSN is linked to only one person.
        - These are pretty rare in practice. Some other examples are country-flag or person-passport
    - [One to many](https://docs.djangoproject.com/en/2.2/ref/models/fields/#foreignkey) example — one student can sign up for many classes, or one job position can have many employees (many software engineers in a company)
        - This is really common (and is [the default](https://docs.djangoproject.com/en/2.2/ref/models/fields/#foreignkey))
    - [Many to many](https://docs.djangoproject.com/en/2.2/ref/models/fields/#manytomanyfield) example — In a list of books and authors, each book can have more than one author and each author can write more than one book. Other examples are doctors and patients, employees and tasks
- [Normalization](https://en.wikipedia.org/wiki/Database_normalization) is the process of structuring a relational database, but we won't do that here...

### Reviews Model

- If we link a user to a review, then we'll use a one to many relationship.
- If we link books to reviews it would be many to many.
- Since it's simpler, we'll treat the reviews app as one to many between authors and reviews.
- Start by adding the `Reviews` model to the `books` app

    ```python
    # books/models.py
    import uuid
    from django.contrib.auth import get_user_model
    from django.db import models
    from django.urls import reverse
    ...
    class Review(models.Model):
      book = models.ForeignKey(
          Book,
          on_delete=models.CASCADE,
          related_name='reviews',
      )
      review = models.CharField(max_length=255)
      author = models.ForeignKey(
          get_user_model(),
          on_delete=models.CASCADE,
      )

      def __str__(self):
        return self.review
    ```

    - Note: since we're using a one-to-many relationship, every many-to-one relationship requires an `[on_delete](https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.ForeignKey.on_delete)` option
- `makemigrations books`, then `migrate`

### Admin

- Add the `Review` model and specify a display of [`TabularInline`](https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#django.contrib.admin.TabularInline)
- Updated `admin.py`

    ```python
    # books/admin.py
    from django.contrib import admin
    from .models import Book, Review

    class ReviewInline(admin.TabularInline):
      model = Review

    class BookAdmin(admin.ModelAdmin):
      inlines = [
          ReviewInline,
      ]
      list_display = ("title", "author", "price",)

    admin.site.register(Book)
    ```

- Create a new user in admin to make comments
- Add two reviews for a book with the new user

### Templates

- Add a basic "Reviews" section and then loop over all existing reviews
- Updated `book_detail.html`

    ```html
    <!-- templates/books/book_detail.html -->
    {% extends '_base.html' %}

    {% block title %}{{ book.title }}{% endblock title %}

    {% block content %}
    <div class="book-detail">
      <h2><a href="">{{ book.title }}</a></h2>
      <p>Author: {{ book.author }}</p>
      <p>Price: {{ book.price }}</p>
      <div class="book-reviews">
        <h3>Reviews</h3>
        <ul>
          {% for review in book.reviews.all %}
          <li>{{ review.review }} ({{ review.author }})</li>
          {% endfor %}
        </ul>
      </div>
    </div>
    {% endblock content %}
    ```

## Tests

- Test review flow
- Updated `tests.py`

    ```python
    # books/tests.py
    from django.contrib.auth import get_user_model
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

            self.book = Book.objects.create(
                title='Harry Potter',
                author='JK Rowling',
                price='25.00',
            )

            self.review = Review.objects.create(
                book=self.book,
                author=self.user,
                review='An excellent review',
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
            self.assertContains(response, 'An excellent review')
            self.assertTemplateUsed(response, 'books/book_detail.html')
    ```

- Run tests