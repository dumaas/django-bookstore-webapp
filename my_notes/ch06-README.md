## Staticfiles App

- set `STATIC_URL = '/static/'` in `bookstore_project/settings.py`
- set `STATICFILES_DIRS` to define location of static files in *local* development

    ```python
    # bookstore_project/settings.py
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),] # new
    ```

- set `STATIC_ROOT` to define location of static files for *production*

    ```python
    # bookstore_project/settings.py
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # new
    ```

    - Note: later we can use the `[collectstatic](https://docs.djangoproject.com/en/2.2/ref/contrib/staticfiles/#django-admin-collectstatic)` command to auto-compile all static files from the entire project into one directory. This is SUPER convenient!
- set `STATICFILES_FINDERS` to tell Django how to look for static file directories.

    ```python
    # bookstore_project/settings.py
    STATICFILES_FINDERS = [
      "django.contrib.staticfiles.finders.FileSystemFinder",
      "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    ]
    ```

### Final code for `bookstore_project/settings.py`

- Code

    ```python
    # bookstore_project/settings.py
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_FINDERS = [
      "django.contrib.staticfiles.finders.FileSystemFinder",
      "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    ]
    ```

## Static Directory

### Create static file tree

- `mkdir static`
- `mkdir static/css`
- `mkdir static/js`
- `mkdir static/images`

### Create `base.css`

- Code

    ```css
    h1 {
      color: red;
    }
    ```

- Set `_base.html` to auto-load static files

    ```html
    <!-- templates/_base.html -->
    {% load static %}
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>{% block title %}Bookstore{% endblock %}</title>
      <!-- CSS -->
      <link rel="stylesheet" href="{% static 'css/base.css' %}">
    </head>
    ```

## Add an Image

- Update `templates/home.html` to display the cover for this book at the bottom of the page!
- Add `{% load static %}` at the top and next to the `<img>` link for the file

    ```html
    <!-- templates/home.html -->
    {% extends '_base.html' %}
    {% load static %}

    {% block title %}Home{% endblock title %}

    {% block content %}
    <h1>Homepage</h1>
    <img class="bookcover" src="{% static 'images/djangoforprofessionals.jpg' %}">
    {% if user.is_authenticated %}
      <p>Hi {{ user.email }}!</p>
      <p><a href="{% url 'logout' %}">Log Out</a></p>
    {% else %}
      <p>You are not logged in</p>
      <p><a href="{% url 'login' %}">Log In</a> |
        <a href="{% url 'signup' %}">Sign Up</a></p>
    {% endif %}
    {% endblock content %}
    ```

### Resize the Image with CSS

- Updated `base.css`

    ```css
    /* static/css/base.css */
    h1 {
      color: red;
    }

    /* new */
    .bookcover {
      height: 300px;
      width: auto;
    }
    ```

## JavaScript

### Create `base.js`

- Code

    ```jsx
    // static/js/base.js
    console.log('Captain JavaScript reporting for duty, sir!')
    ```

    - Note: this is often good for tracking codes (for Google Analytics)
- Set `_base.html` to auto-load JS

    ```html
    <!-- templates/_base.html -->
    {% load static %}
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>{% block title %}Bookstore{% endblock title %}</title>
      <!-- CSS -->
      <link rel="stylesheet" href="{% static 'css/base.css' %}">
    </head>
    <body>
      <div class="container">
        {% block content %}
        {% endblock content %}
      </div>
      <!-- JavaScript -->
      {% block javascript %}
      <script src="{% static 'js/base.js' %}"></script>
      {% endblock javascript %}
    </body>
    </html>
    ```

    - Note: Render JS at the bottom of the file so that the page appears to load faster.
- Note: to see the `console.log()` output, open up devtools and go to the console area.

## Run CollectStatic to Deploy

- Run `docker-compose exec web python manage.py collectstatic` to compile all static files into one directory for deploying the site

## Bootstrap

- Bootstrap is a great framework for the early iterations of your site! You can always go back and write custom CSS later.
- Note: Order matters. Make sure to load the bootstrap file *before* `base.css` so that our custom css will override the bootstrap config. At the bottom, be sure to load jQuery, then PopperJS, then Bootstrap JavaScript

### Add Bootstrap to `_base.html`

- Updated `_base.html`

    ```html
    {% load static %}
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>{% block title %}Bookstore{% endblock title %}</title>
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
      <!-- CSS -->
      <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
      <link rel="stylesheet" href="{% static 'css/base.css' %}">
    </head>
    <body>
      <header>
        <!-- Fixed navbar -->
        <div class="d-flex flex-column flex-md-row align-items-center p-3 px-md-4
         mb-3 bg-white border-bottom shadow-sm">
          <a href="{% url 'home' %}" class="navbar-brand my-0 mr-md-auto
          font-weight-normal">Bookstore</a>
          <nav class="my-2 my-md-0 mr-md-3">
            <a class="p-2 text-dark" href="{% url 'about' %}">About</a>
            {% if user.is_authenticated %}
              <a class="p-2 text-dark" href="{% url 'logout' %}">Log Out</a>
            {% else %}
              <a class="p-2 text-dark" href="{% url 'login' %}">Log In</a>
              <a class="btn btn-outline-primary"
                href="{% url 'signup' %}">Sign Up</a>
            {% endif %}
          </nav>
        </div>
      </header>
      <div class="container">
        {% block content %}
        {% endblock content %}
      </div>
      <!-- JavaScript -->
      <!-- JS, Popper.js, and jQuery -->
      <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
      <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js" integrity="sha384-9/reFTGAW83EW2RDu2S0VKaIzap3H66lZH81PoYlFhbGU+6BZp6G7niu735Sk7lN" crossorigin="anonymous"></script>
      <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.bundle.min.js" integrity="sha384-1CmrxMRARb6aLqgBO7yyAxTOQE2AKb9GfXnEo760AUcUmFx3ibVJJAzGytlQcNXd" crossorigin="anonymous"></script>
    </body>
    </html>
    ```

## Create the About Page

### Template

- Code for `templates/about.html`

    ```html
    <!-- templates/about.html -->
    {% extends '_base.html' %}

    {% block title %}About{% endblock title %}

    {% block content %}
    <h1>About Page</h1>
    {% endblock content %}
    ```

### View

- Code for `pages/views.py`

    ```python
    # pages/views.py
    from django.views.generic import TemplateView

    class HomePageView(TemplateView):
      template_name = 'home.html'

    class AboutPageView(TemplateView): # new
      template_name = 'about.html'
    ```

### URL

- Code for `pages/urls.py`

    ```python
    # pages/urls.py
    from django.urls import path

    from .views import HomePageView, AboutPageView

    urlpatterns = [
        path('about/', AboutPageView.as_view(), name='about'), # new
        path('', HomePageView.as_view(), name='home'),
    ]
    ```

## Django Crispy Forms

### Install with Docker

- Install with Docker: `docker-compose exec web pipenv install django-crispy-forms`
- Stop the container: `docker-compose down`
- Rebuild it: `docker-compose up -d --build`

### Config for crispy-forms

- Add crispy forms to `INSTALLED_APPS`, specify bootstrap for `CRISPY_TEMPLATE_PACK`

    ```python
    # bookstore_project/settings.py
    INSTALLED_APPS = [
      'django.contrib.admin',
      'django.contrib.auth',
      'django.contrib.contenttypes',
      'django.contrib.sessions',
      'django.contrib.messages',
      'django.contrib.staticfiles',
      
      # Third-party
      'crispy_forms', # new
      
      # Local
      'users.apps.UsersConfig',
      'pages.apps.PagesConfig',
    ]
    # django-crispy-forms
    CRISPY_TEMPLATE_PACK = 'bootstrap4' # new
    ```

- Load `crispy_forms_tags` at the top of a template and replace `{{ form.as_p }}` with `{{ form|crispy }}` for all form fields
    - Updated `templates/registration/signup.html`

        ```html
        <!-- templates/signup.html -->
        {% extends '_base.html' %}
        {% load crispy_forms_tags %}

        {% block title %}Sign Up{% endblock title %}

        {% block content %}
        <h2>Sign Up</h2>
        <form method="post">
          {% csrf_token %}
          {{ form|crispy }}
          <button class="btn btn-success" type="submit">Sign Up</button>
        </form>
        {% endblock content %}
        ```

    - Updated `templates/registration/login.html`

        ```html
        <!-- templates/registration/login.html -->
        {% extends '_base.html' %}
        {% load crispy_forms_tags %}

        {% block title %}Log In{% endblock title %}

        {% block content %}
        <h2>Log In</h2>
        <form method="post">
          {% csrf_token %}
          {{ form|crispy }}
          <button class="btn btn-success" type="submit">Log In</button>
        </form>
        {% endblock content %}
        ```

## Add New Tests

- Updated `pages/tests.py`

    ```python
    from django.test import SimpleTestCase
    from django.urls import reverse, resolve

    from .views import HomePageView, AboutPageView # new

    class HomepageTests(SimpleTestCase):
      ...

    class AboutPageTests(SimpleTestCase):
      def setUp(self):
        url = reverse('about')
        self.response = self.client.get(url)

      def test_aboutpage_status_code(self):
        self.assertEqual(self.response.status_code, 200)

      def test_aboutpage_template(self):
        self.assertTemplateUsed(self.response, 'about.html')

      def test_aboutpage_contains_correct_html(self):
        self.assertContains(self.response, 'About Page')

      def test_aboutpage_does_not_contain_incorrect_html(self):
        self.assertNotContains(
            self.response, 'Hi there! I should not be on the page.')

      def test_aboutpage_url_resolves_aboutpageview(self):
        view = resolve('/about/')
        self.assertEqual(
            view.func.__name__,
            AboutPageView.as_view().__name__,
        )
    ```

- Run tests: `docker-compose exec web python manage.py test`