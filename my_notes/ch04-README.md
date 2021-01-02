## Basic Setup

- `docker-compose exec web python manage.py startapp pages`, add to `INSTALLED_APPS`
    - Code

        ```python
        # bookstore_project/settings.py
        INSTALLED_APPS = [
          ...
          # Local
          'users.apps.UsersConfig',
          'pages.apps.PagesConfig', # new
        ]
        ...
        TEMPLATES = [
          {
            ...
            'DIRS': [os.path.join(BASE_DIR, 'templates')], # new
            ...
        }
        ```

- `mkdir templates`, `touch templates/_base.html && touch templates/home.html`
    - Note: The underscore in `_base.html` denotes that this file is intended to be inherited by other files and not displayed on its own.
    - Code for `_base.html`

        ```html
        <!-- templates/_base.html -->
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>{% block title %}Bookstore{% endblock title %}</title>
        </head>
        <body>
          <div class="container">
            {% block content %}
            {% endblock content %}
          </div>
        </body>
        </html>
        ```

    - Code for `home.html`

        ```html
        <!-- templates/home.html -->
        {% extends '_base.html' %}

        {% block title %}Home{% endblock title %}

        {% block content %}
        <h1>Homepage</h1>
        {% endblock content %}
        ```

## URLs and Views

- Code for urls.py

    ```python
    # bookstore_project/urls.py
    from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', include('pages.urls')),
    ]
    ```

    ```python
    # pages/urls.py
    from django.urls import path
    from .views import HomePageView

    urlpatterns = [
        path('', HomePageView.as_view(), name='home')
    ]
    ```

- Code for views.py

    ```python
    # pages/views.py
    from django.views.generic import TemplateView

    class HomePageView(TemplateView):
      template_name = 'home.html'
    ```

- Reload the `books` app with `docker-compose down` and then `docker-compose up -d`

## Tests

- Since our homepage doesn't use a model currently, we can use [SimpleTestCase](https://docs.djangoproject.com/en/2.2/topics/testing/tools/#simpletestcase)
    - Code for `pages/tests.py`

        ```python
        # pages/tests.py
        from django.test import SimpleTestCase
        from django.urls import reverse

        class HomepageTests(SimpleTestCase):
          def test_homepage_status_code(self):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)

          def test_homepage_url_name(self):
            response = self.client.get(reverse('home'))
            self.assertEqual(response.status_code, 200)
        ```

- Run tests: `docker-compose exec web python manage.py test`

## Testing Templates

- Use [assertTemplateUsed](https://docs.djangoproject.com/en/2.2/topics/testing/tools/#django.test.SimpleTestCase.assertTemplateUsed) to confirm that the homepage uses the right template
    - Updated code for `pages/tests.py`

        ```python
        # pages/tests.py
        from django.test import SimpleTestCase
        from django.urls import reverse

        class HomepageTests(SimpleTestCase):
          def test_homepage_status_code(self):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)

          def test_homepage_url_name(self):
            response = self.client.get(reverse('home'))
            self.assertEqual(response.status_code, 200)

          def test_homepage_template(self):
            response = self.client.get('/')
            self.assertTemplateUsed(response, 'home.html')
        ```

- Run tests: `docker-compose exec web python manage.py test pages`

## Testing HTML

- Add tests to confirm that the homepage uses the right HTML code and doesn't have incorrect text
    - Updated code for `pages/tests.py`

        ```python
        # pages/tests.py
        from django.test import SimpleTestCase
        from django.urls import reverse, resolve

        from .views import HomePageView

        class HomepageTests(SimpleTestCase):
          def test_homepage_status_code(self):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)

          def test_homepage_url_name(self):
            response = self.client.get(reverse('home'))
            self.assertEqual(response.status_code, 200)

          def test_homepage_template(self):
            response = self.client.get('/')
            self.assertTemplateUsed(response, 'home.html')

          def test_homepage_contains_correct_html(self):
            response = self.client.get('/')
            self.assertContains(response, 'Homepage')

          def test_homepage_does_not_contain_incorrect_html(self):
            response = self.client.get('/')
            self.assertNotContains(
                response, 'Hi there! I should not be on the page.'
            )
        ```

- Run tests: `docker-compose exec web python manage.py test pages`

## setUp Method

- So far we've been repeating a LOT within the tests. Is there something more DRY (Don't Repeat Yourself) that we could be doing?
    - Updated `tests.py` with `setUp` method

        ```python
        # pages/tests.py
        from django.test import SimpleTestCase
        from django.urls import reverse

        class HomepageTests(SimpleTestCase):
          def setUp(self):
            url = reverse('home')
            self.response = self.client.get(url)

          def test_homepage_status_code(self):
            self.assertEqual(self.response.status_code, 200)

          def test_homepage_template(self):
            self.assertTemplateUsed(self.response, 'home.html')

          def test_homepage_contains_correct_html(self):
            self.assertContains(self.response, 'Homepage')

          def test_homepage_does_not_contain_incorrect_html(self):
            self.assertNotContains(
                self.response, 'Hi there! I should not be on the page.'
            )
        ```

- Run tests: `docker-compose exec web python manage.py test pages`

## Resolve

- Check that the name of the view used to resolve '/' matches `HomePageView` with the [resolve](https://docs.djangoproject.com/en/2.2/ref/urlresolvers/#resolve) function
    - Updated `tests.py` with `resolve` function

        ```python
        # pages/tests.py
        from django.test import SimpleTestCase
        from django.urls import reverse, resolve

        from .views import HomePageView

        class HomepageTests(SimpleTestCase):
          def setUp(self):
            url = reverse('home')
            self.response = self.client.get(url)

          def test_homepage_status_code(self):
            self.assertEqual(self.response.status_code, 200)

          def test_homepage_template(self):
            self.assertTemplateUsed(self.response, 'home.html')

          def test_homepage_contains_correct_html(self):
            self.assertContains(self.response, 'Homepage')

          def test_homepage_does_not_contain_incorrect_html(self):
            self.assertNotContains(
                self.response, 'Hi there! I should not be on the page.'
            )

          def test_homepage_url_resolves_homepageview(self): # new
            view = resolve('/')
            self.assertEqual(
                view.func.__name__,
                HomePageView.as_view().__name__,
            )
        ```

- Run FINAL tests: `docker-compose exec web python manage.py test pages`