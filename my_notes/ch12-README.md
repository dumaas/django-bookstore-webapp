## [Pillow](https://python-pillow.org/) Setup

- User-uploaded files are considered `media` by Django, whereas static assets are considered `static`.
- Install Pillow, then re-spin Docker (uppercase Pillow matters!!)
    - `docker-compose exec web pipenv install Pillow`
    - Make sure to add the `--build` tag when starting Docker again...

### Media Files

- The main difference between `static` and `media` files is that we can 100% trust static files (since we upload them!) but we can't trust media files by default.
    - There are ALWAYS [security concerns](https://docs.djangoproject.com/en/2.2/ref/models/fields/#file-upload-security) with [user-uploaded content](https://docs.djangoproject.com/en/2.2/topics/security/#user-uploaded-content)
- It's always important to VALIDATE uploaded files to ensure they are what they say they are.
- First, configure `MEDIA_ROOT` and `MEDIA_URL` in `settings.py`

    ```python
    # bookstore_project/settings.py
    MEDIA_URL = '/media/' # new
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # new
    ```

    - `MEDIA_ROOT` — absolute file path to dir for user-uploaded files
    - `MEDIA_URL` — url to be used in templates for these files
- Then create the `media` dir, then `media/covers/`
- Update `[urls.py](http://urls.py)` to show media items locally

    ```python
    # bookstore_project/urls.py
    from django.conf import settings
    from django.conf.urls.static import static
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
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    ```

### Models

- Store images with [ImageField](https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.ImageField)
- Updated `models.py`

    ```python
    # books/models.py
    class Book(models.Model):
      id = models.UUIDField(
          primary_key=True,
          default=uuid.uuid4,
          editable=False)
      title = models.CharField(max_length=200)
      author = models.CharField(max_length=200)
      price = models.DecimalField(max_digits=6, decimal_places=2)
      cover = models.ImageField(upload_to='covers/', blank=True) # new
    ```

- Makemigrations, migrate

### Admin

- Upload images for book covers

### Template

- Update `book_detail.html` to display book cover on individual pages

    ```html
    <!-- book_detail.html -->
    {% extends '_base.html' %}

    {% block title %}{{ book.title }}{% endblock title %}

    {% block content %}
    <div class="book-detail">
      <img class="bookcover" src="{{ book.cover.url }}" alt="{{ book.title }}">
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

- One potential issue is that the template now EXPECTS a cover to be present...
- Update `book_detail.html` to fix this!

    ```html
    <!-- book_detail.html -->
    {% extends '_base.html' %}

    {% block title %}{{ book.title }}{% endblock title %}

    {% block content %}
    <div class="book-detail">
      {% if book.cover %}
        <img class="bookcover" src="{{ book.cover.url }}" alt="{{ book.title }}">
      {% endif %}
    ...
    ```

### Next Steps

- Add a dedicated create/edit/delete forms for creating books and cover images
- Add a LOT of extra validations for the image-uploading
- Store `media` files in a dedicated CDN (content delivery network) for extra security
    - This could also help performance on large sites for `static` files, but for `media` files this is a good idea regardless of size.
    - Possible guide on doing this with Whitenoise [here](https://medium.com/technolingo/fastest-static-files-served-django-compressor-whitenoise-aws-cloudfront-ef777849090c), be sure to set up with Cloudflare for optimal performance
    - Nginx is a popular alternative
- Finally, tests would be nice to have here, but they would be primarily focused on the form validation section (not the basic image-uploading in admin)