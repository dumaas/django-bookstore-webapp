### General Advice

- Performance usually comes down to:
    - optimizing database queries
    - caching
    - indexes
    - compressing front-end assets like images, JS, and CSS

## [django-debug-toolbar](https://github.com/jazzband/django-debug-toolbar)

- `pipenv install django-debug-toolbar`
    - Then close the Docker container
- Update `INSTALLED_APPS`, `Middleware`, and `INTERNAL_IPS` in `settings.py`

    ```python
    # bookstore_project/settings.py
    import socket
    INSTALLED_APPS = [
      'django.contrib.admin',
      'django.contrib.auth',
      'django.contrib.contenttypes',
      'django.contrib.sessions',
      'django.contrib.messages',
      'django.contrib.staticfiles',
      'django.contrib.sites',
      # Third-party
      'crispy_forms',
      'allauth',
      'allauth.account',
      'debug_toolbar', # new
      # Local
      'users.apps.UsersConfig',
      'pages.apps.PagesConfig',
      'books.apps.BooksConfig',
      'orders.apps.OrdersConfig',
    ]
    ...
    MIDDLEWARE = [
      'django.middleware.security.SecurityMiddleware',
      'django.contrib.sessions.middleware.SessionMiddleware',
      'django.middleware.common.CommonMiddleware',
      'django.middleware.csrf.CsrfViewMiddleware',
      'django.contrib.auth.middleware.AuthenticationMiddleware',
      'django.contrib.messages.middleware.MessageMiddleware',
      'django.middleware.clickjacking.XFrameOptionsMiddleware',
      'debug_toolbar.middleware.DebugToolbarMiddleware', # new
    ]
    ...
    # django-debug-toolbar
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[:-1] + "1" for ip in ips]
    ```

- rebuild Docker
- Update `[urls.py](http://urls.py)` so that Debug Toolbar only shows if `DEBUG=True`

    ```python
    # bookstore_project/urls.py
    ...
    if settings.DEBUG:
      import debug_toolbar
      urlpatterns = [
          path('__debug__/', include(debug_toolbar.urls)),
      ] + urlpatterns
    ```

### Analyzing Pages

- Debug Toolbar has [a LOT of customizations](https://django-debug-toolbar.readthedocs.io/en/latest/index.html)
- One of the most useful items is `SQL` which shows which queries are being run and the time for each of them

### [select_related](https://docs.djangoproject.com/en/2.2/ref/models/querysets/#select-related) and [prefetch_related](https://docs.djangoproject.com/en/2.2/ref/models/querysets/#prefetch-related)

- `select_related` is used for single-value relationships through a forward one to many or one to one relationship. It creates a SQLjoin and inlcudes the fields of the related object in the `select` statement, which results in all related objects being included in a single more complex database query. This single query is usually more performant than multiple, smaller queries.
- `prefetch_related` is used for a set or list of objects like a many to many or many to one relationship.
- Implementing one or both of these is a common first pass towards reducing queries and load time for a page

### Caching

- [Memcached](https://docs.djangoproject.com/en/2.2/topics/cache/#memcached) and [django-redis](https://github.com/niwinz/django-redis) are popular options for this
- Django also has [its own cache framework](https://docs.djangoproject.com/en/2.2/topics/cache/) with four caching options:
    1. [per-site cache](https://docs.djangoproject.com/en/2.2/topics/cache/#the-per-site-cache) — simplest to set up and caches the entire site
    2. [per-view cache](https://docs.djangoproject.com/en/2.2/topics/cache/#the-per-view-cache)
    3. [Template fragment caching](https://docs.djangoproject.com/en/2.2/topics/cache/#template-fragment-caching) — specify a segment of a template to cache
    4. [low-level cache API](https://docs.djangoproject.com/en/2.2/topics/cache/#the-low-level-cache-api) — manually set, retrieve, and maintain specific objects in the cache
- The caching needs to be accurate, but not wasteful. This takes a good bit of fine-tuning to get just right.
- Add per-site caching within `settings.py`

    ```python
    # bookstore_project/settings.py
    MIDDLEWARE = [
      'django.middleware.cache.UpdateCacheMiddleware', # new
      'django.middleware.security.SecurityMiddleware',
      'django.contrib.sessions.middleware.SessionMiddleware',
      'django.middleware.common.CommonMiddleware',
      'debug_toolbar.middleware.DebugToolbarMiddleware',
      'django.middleware.csrf.CsrfViewMiddleware',
      'django.contrib.auth.middleware.AuthenticationMiddleware',
      'django.contrib.messages.middleware.MessageMiddleware',
      'django.middleware.clickjacking.XFrameOptionsMiddleware',
      'debug_toolbar.middleware.DebugToolbarMiddleware',
      'django.middleware.cache.FetchFromCacheMiddleware', # new
    ]
    ...
    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_SECONDS = 604800
    CACHE_MIDDLEWARE_KEY_PREFIX = ''
    ```

- Note: you may want to adjust the caching time...

### [Indexes](https://en.wikipedia.org/wiki/Database_index)

- Common way to speed up database performance
    - Typically only applied to the primary key in a model
- The only downside of indexes is that they require extra space on the disk
- General rule: if a given field is being used frequently, like 10-25% of all queries, then index it!
- Update `books/models.py` to add indexing!

    ```python
    # books/models.py
    ...
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
            indexes = [ # new
                models.Index(fields=['id'], name='id_index'),
            ]
    ...
    ```

- `makemigrations`, then `migrate`

### [django-extensions](https://github.com/django-extensions/django-extensions)

- This package is popular for inspecting a Django project because of all of the [custom extentions](https://django-extensions.readthedocs.io/en/latest/command_extensions.html) it adds!
- The `[shell_plus](https://django-extensions.readthedocs.io/en/latest/shell_plus.html)` extention autoloads all models into the shell, which makes working with the Django ORM muccccch easier

### Front-end Assets

- [django-compression](https://github.com/django-compressor/django-compressor) can help reduce the size of CSS and JS files
- [easy-thumbnails](https://github.com/SmileyChris/easy-thumbnails) can serve smaller image files when possible, which can help a lot!
- Check out [Essential Image Optimization](https://images.guide/) by Addy Osmani
- Using automated tests for front-end speed like with Google's [PageSpeed Insights](https://developers.google.com/speed/pagespeed/insights/)