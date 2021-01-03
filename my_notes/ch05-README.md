## Log-in and Log-out with the [Auth App](https://docs.djangoproject.com/en/2.2/topics/auth/default/)

- Notice that Django's auth app is automatically installed in `settings.py`

    ```python
    # bookstore_project/settings.py
    INSTALLED_APPS = [
      'django.contrib.admin',
      'django.contrib.auth', # Yoohoo!!!!
      'django.contrib.contenttypes',
      'django.contrib.sessions',
      'django.contrib.messages',
      'django.contrib.staticfiles',
      # Local
      'users.apps.UsersConfig',
      'pages.apps.PagesConfig',
    ]
    ```

- Add the built-in `auth` app to `bookstore_project/urls.py`

    ```python
    # bookstore_project/urls.py
    from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
        # Django admin
        path('admin/', admin.site.urls),

        # User management
        path('accounts/', include('django.contrib.auth.urls')),

        # Local apps
        path('', include('pages.urls')),
    ]
    ```

    - List of URLs associated with the `auth` app

        ```
        accounts/login/ [name='login']
        accounts/logout/ [name='logout']
        accounts/password_change/ [name='password_change']
        accounts/password_change/done/ [name='password_change_done']
        accounts/password_reset/ [name='password_reset']
        accounts/password_reset/done/ [name='password_reset_done']
        accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
        accounts/reset/done/ [name='password_reset_complete']
        ```

## Homepage

- Update the homepage to notify us if a user is already logged in or not
    - New code for `templates/home.html`

        ```html
        <!-- templates/home.html -->
        {% extends '_base.html' %}

        {% block title %}Home{% endblock title %}

        {% block content %}
        <h1>Homepage</h1>
        {% if user.is_authenticated %}
          Hi {{ user.email }}!
        {% else %}
          <p>You are not logged in</p>
          <a href="{% url 'login' %}">Log In</a>
        {% endif %}
        <p>
          <a href="https://github.com/dumaas/books-app" target="_blank">Click here</a> to see the source code for this project!
        </p>
        {% endblock content %}
        ```

## [Django Source Code](https://docs.djangoproject.com/en/2.2/topics/auth/default/)

- How was the `user` and its variables magically available to the template?
    - Django's [template context](https://docs.djangoproject.com/en/2.2/topics/auth/default/#authentication-data-in-templates) feature means that each template is loaded with data from the corresponding `views.py` file. This allows us to use `user` in template tags to access User attributes.
    - We used `user.is_authenticated` to return a boolean value depending on if the user was logged in
    - We used the URL name `login` in `{% url 'login' %}` (a [url template tag](https://docs.djangoproject.com/en/2.2/ref/templates/builtins/#url)) which takes a [named URL pattern](https://docs.djangoproject.com/en/2.2/topics/http/urls/#naming-url-patterns) as its first argument — this is the optional `name` section we use when defining URL paths in each `urls.py`
- Great process for learning Django as you go along:
    1. Remembering the Django shortcut
    2. Look it up in [the documentation](https://docs.djangoproject.com/en/3.1/)
    3. Dive deep into the [source code](https://github.com/django/django) to truly understand where the magic happens.

## Log In

- Clicking on the `log in` button brings us to an error page...why?
    - Django expects a log-in template at `registration/login.html`. We can also look at the [documentation](https://docs.djangoproject.com/en/2.2/topics/auth/default/#all-authentication-views) and see that the desired `template_name` has that location
    - Why is this? Into the source code we go!
        - In `[auth/views.py](https://github.com/django/django/blob/b9cf764be62e77b4777b3a75ec256f6209a57671/django/contrib/auth/views.py)`, for `LoginView` the `template_name` is '`registration/login.html`'. We COULD change the default location by overriding `LoginView`, but that's a little overkill.
    - To fix this, create a `registration` dir within the `templates` directory, then create `registration/login.html`
        - Code for `templates/registration/login.html`

            ```html
            <!-- templates/registration/login.html -->
            {% extends '_base.html' %}

            {% block title %}Log In{% endblock title %}

            {% block content %}
            <h2>Log In</h2>
            <form method="post">
              {% csrf_token %}
              {{ form.as_p }}
              <button type="submit">Log In</button>
            </form>
            {% endblock content %}
            ```

            - Note: ALWAYS add [CSRF protection](https://docs.djangoproject.com/en/2.2/ref/csrf/) on any submittable form. Do this easily with `{% csrf_token %}` tags at the start of any form.
            - Control the form contents with `[as_p](https://docs.djangoproject.com/en/2.2/ref/forms/api/#as-p)` so that each form field is displayed within a paragraph `<p>` tag.

## Redirects

- Right now the login page works, but it redirects us to a URL that doesn't exist. (`accounts/profile`)
    - To fix this, properly configure the [LOGIN_REDIRECT_URL](https://docs.djangoproject.com/en/2.2/ref/settings/#login-redirect-url) to redirect to the homepage
        - Updated `settings.py`

            ```python
            # bookstore_project/settings.py
            LOGIN_REDIRECT_URL = 'home'
            ```

## Log Out

- Configure LOGOUT_REDIRECT_URL to redirect to the homepage after logging out
    - Updated `settings.py`

        ```python
        # bookstore_project/settings.py
        LOGIN_REDIRECT_URL = 'home'
        LOGOUT_REDIRECT_URL = 'home'
        ```

- Add the logout link to `templates/home.html`
    - Code

        ```html
        <!-- templates/home.html -->
        {% extends '_base.html' %}

        {% block title %}Home{% endblock title %}

        {% block content %}
        <h1>Homepage</h1>
        {% if user.is_authenticated %}
          Hi {{ user.email }}!
          <p><a href="{% url 'logout %}">Log Out</a></p> <!-- new -->
        {% else %}
          <p>You are not logged in</p>
          <a href="{% url 'login' %}">Log In</a>
        {% endif %}
        <p>
          <a href="https://github.com/dumaas/books-app" target="_blank">Click here</a> to see the source code for this project!
        </p>
        {% endblock content %}
        ```

## Sign Up

- URLs

    ```python
    # users/urls.py
    from django.urls import path

    from .views import SignupPageView

    urlpatterns = [
        path('signup/', SignupPageView.as_view(), name='signup'),
    ]
    ```

    ```python
    # bookstore_project/urls.py
    from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
        # Django admin
        path('admin/', admin.site.urls),

        # User management
        path('accounts/', include('django.contrib.auth.urls')),

        # Local apps
        path('accounts/', include('users.urls')), # new
        path('', include('pages.urls')),
    ]
    ```

- Views

    ```python
    # users/views.py
    from django.urls import reverse_lazy
    from django.views import generic

    from .forms import CustomUserCreationForm

    class SignupPageView(generic.CreateView):
      form_class = CustomUserCreationForm
      success_url = reverse_lazy('login')
      template_name = 'signup.html'
    ```

- Templates

    ```html
    <!-- templates/signup.html -->
    {% extends '_base.html' %}

    {% block title %}Sign Up{% endblock title %}

    {% block content %}
    <h2>Sign Up</h2>
    <form method="post">
      {% csrf_token %}
      {{ form.as_p }}
      <button type="submit">Sign Up</button>
    </form>
    {% endblock content %}
    ```

    ```html
    <!-- templates/home.html -->
    {% extends '_base.html' %}

    {% block title %}Home{% endblock title %}

    {% block content %}
    <h1>Homepage</h1>
    {% if user.is_authenticated %}
      Hi {{ user.email }}!
      <p><a href="{% url 'logout' %}">Log Out</a></p>
    {% else %}
      <p>You are not logged in</p>
      <a href="{% url 'login' %}">Log In</a>
      <a href="{% url 'signup' %}">Sign Up</a> <!-- new -->
    {% endif %}
    <p>
      <a href="https://github.com/dumaas/books-app" target="_blank">Click here</a> to see the source code for this project!
    </p>
    {% endblock content %}
    ```

- Create a new user with email `testuser@email.com`, username `testuser`,

## Tests

- Note: We DON'T need to test the log-in and log-out functionality, since those are built into Django and already have tests. We DO need testing for the sign-up functionality!
    - Code to test status code, template used, and included/excluded text

        ```python
        # users/tests.py
        from django.contrib.auth import get_user_model
        from django.test import TestCase
        from django.urls import reverse # new

        ...

        class SignupPageTests(TestCase):
            def setUp(self):
                url = reverse('signup')
                self.response = self.client.get(url)

            def test_signup_template(self):
                self.assertEqual(self.response.status_code, 200)
                self.assertTemplateUsed(self.response, 'signup.html')
                self.assertContains(self.response, 'Sign Up')
                self.assertNotContains(
                        self.response, 'Hi there! I should not be here...')
        ```

    - Run tests: `docker-compose exec web python manage.py test users`
- Next, test `CustomUserCreationForm` is being used and that the page resolves to `SignupPageView`
    - Updated `users/tests.py`

        ```python
        # users/tests.py
        from django.contrib.auth import get_user_model
        from django.test import TestCase
        from django.urls import reverse, resolve # new

        from .forms import CustomUserCreationForm # new
        from .views import SignupPageView # new

        ...

        class SignupPageTests(TestCase):
            def setUp(self):
                url = reverse('signup')
                self.response = self.client.get(url)

            def test_signup_template(self):
                self.assertEqual(self.response.status_code, 200)
                self.assertTemplateUsed(self.response, 'signup.html')
                self.assertContains(self.response, 'Sign Up')
                self.assertNotContains(
                        self.response, 'Hi there! I should not be here...')

            def test_signup_form(self): # new
                form = self.response.context.get('form')
                self.assertIsInstance(form, CustomUserCreationForm)
                self.assertContains(self.response, 'csrfmiddlewaretoken')

            def test_signup_view(self): # new
                view = resolve('/accounts/signup/')
                self.assertEqual(
                    view.func.__name__,
                    SignupPageView.as_view().__name__,
                )
        ```

    - Run tests: `docker-compose exec web python manage.py test users`
- Note: [`setUpTestData()`](https://docs.djangoproject.com/en/2.2/topics/testing/tools/#django.test.TestCase.setUpTestData) is a more optimal test you can use if tests are running too slowly!