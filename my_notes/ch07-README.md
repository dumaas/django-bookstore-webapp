## [django-allauth](https://github.com/pennersr/django-allauth)

- Basic installation
    - `docker-compose exec web pipenv install django-allauth`
    - `docker-compose down`
    - `docker-compose up -d --build`
- Integrate with our app
    - Updated `settings.py`
        - Update `INSTALLED_APPS`
        - Add `SITE_ID`, since django-allauth can control multiple sites!

        ```python
        # bookstore_project/settings.py
        INSTALLED_APPS = [
          'django.contrib.admin',
          'django.contrib.auth',
          'django.contrib.contenttypes',
          'django.contrib.sessions',
          'django.contrib.messages',
          'django.contrib.staticfiles',
          'django.contrib.sites', # new
          
          # Third-party
          'crispy_forms',
          'allauth', # new
          'allauth.account', # new
          
          # Local
          'users.apps.UsersConfig',
          'pages.apps.PagesConfig',
        ]

        # django-allauth config
        SITE_ID = 1 # new
        ```

### `AUTHENTICATION_BACKENDS`

- `bookstore_project/settings.py` only contains the explicit settings for our Django project, but there are more settings behind the scenes.
    - [Complete list of settings configurations](https://docs.djangoproject.com/en/2.2/ref/settings/)
- For django-allauth to work, we need to update the default `[AUTHENTICATION_BACKENDS](https://docs.djangoproject.com/en/2.2/ref/settings/#authentication-backends)` setting.
    - Add specific auth options — this will allow us to switch over to using login via email
- Updated `bookstore_project/settings.py`

    ```python
    # bookstore_project/settings.py
    # django-allauth config
    SITE_ID = 1
    AUTHENTICATION_BACKENDS = (
      'django.contrib.auth.backends.ModelBackend', # default
      'allauth.account.auth_backends.AuthenticationBackend', # new
    )
    ```

### `EMAIL_BACKEND`

- By default, `[EMAIL_BACKEND](https://docs.djangoproject.com/en/2.2/ref/settings/#email-backend)` is configured for a [SMTP server](https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol) to send emails
- Since we don't have a SMTP server setup yet, we'll get an error for user authentication. To avoid this, (temporarily) switch to having Django output emails to the command line [console](https://docs.djangoproject.com/en/2.2/topics/email/#console-backend)
- Updated `bookstore_project/settings.py`

    ```python
    # bookstore_project/settings.py
    # django-allauth config
    SITE_ID = 1

    AUTHENTICATION_BACKENDS = (
      'django.contrib.auth.backends.ModelBackend',
      'allauth.account.auth_backends.AuthenticationBackend',
    )

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # new
    ```

### `ACCOUNT_LOGOUT_REDIRECT`

- django-allauth's [config](https://django-allauth.readthedocs.io/en/latest/configuration.html) actually overrides the built-in `LOGOUT_REDIRECT_URL`...we should future-proof the app a bit by removing the double-definition
- Updated `bookstore_project/settings.py`

    ```python
    # bookstore_project/settings.py
    # django-allauth config
    LOGIN_REDIRECT_URL = 'home'
    ACCOUNT_LOGOUT_REDIRECT = 'home' # new

    SITE_ID = 1

    AUTHENTICATION_BACKENDS = (
      'django.contrib.auth.backends.ModelBackend',
      'allauth.account.auth_backends.AuthenticationBackend',
    )

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    ```

- Finally, migrate the database to update with new settings.
    - `docker-copmose exec web python manage.py migrate`

### URLs

- Swap out the built-in `auth` app for `django-allauth`'s `allauth` app
- Note: since we're using `allauth`'s templates and routes for sign up, we can also delete the URL path for the `users` app
- Updated `bookstore_project/urls.py`

    ```python
    # bookstore_project/urls.py
    from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
      # Django admin
      path('admin/', admin.site.urls),
      
      # User management
      path('accounts/', include('allauth.urls')), # new
      
      # Local apps
      path('', include('pages.urls')),
    ]
    ```

- Be sure to delete `users/urls.py` and `users/views.py` since they're not needed at the moment.

### Templates

- While Django's `auth` app looks for templates in `templates/registration`, `django-allauth` looks for `templates/account`
    - `mkdir templates/account`
    - `mv templates/registration/login.html templates/account/login.html`
    - `mv templates/registration/signup.html templates/account/signup.html`
    - Or just rename the `registration` folder to `account`...
- Update URL links in `templates/_base.html` and `temaplates/home.html` to use `django-allauth`'s URL names instead of Django's.

    ```html
    <!-- templates/_base.html -->
    ...
    <nav class="my-2 my-md-0 mr-md-3">
      <a class="p-2 text-dark" href="{% url 'about' %}">About</a>
      {% if user.is_authenticated %}
        <a class="p-2 text-dark" href="{% url 'account_logout' %}">Log Out</a>
      {% else %}
        <a class="p-2 text-dark" href="{% url 'account_login' %}">Log In</a>
        <a class="btn btn-outline-primary"
          href="{% url 'account_signup' %}">Sign Up</a>
      {% endif %}
    </nav>
    ...
    ```

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
      <p><a href="{% url 'account_logout' %}">Log Out</a></p>
    {% else %}
      <p>You are not logged in</p>
      <p><a href="{% url 'account_login' %}">Log In</a> |
      <a href="{% url 'account_signup' %}">Sign Up</a></p>
    {% endif %}
    {% endblock content %}
    ```

### Log In

- Note: there's not a 'remember me' option...thanks `django-allauth`! This is just one of [many configurations](https://django-allauth.readthedocs.io/en/latest/configuration.html) provided.
- Set `ACCOUNT_SESSION_REMEMBER = True` so that user login info is automatically remembered

    ```python
    # bookstore_project/settings.py
    # django-allauth config
    ...
    ACCOUNT_SESSION_REMEMBER = True # new
    ```

### Log Out

- Create a log out template: `touch templates/account/logout.html`
- New code for `logout.html`

    ```html
    <!-- templates/account/logout.html -->
    {% extends '_base.html' %}
    {% load crispy_forms_tags %}

    {% block title %}Log Out{% endblock %}

    {% block content %}
    <div class="container">
      <h1>Log Out</h1>
      <p>Are you sure you want to log out?</p>
      <form method="post" action="{% url 'account_logout' %}">
        {% csrf_token %}
        {{ form|crispy}}
        <button class="btn btn-danger" type="submit">Log Out</button>
      </form>
    </div>
    {% endblock %}
    ```

### Sign Up

- Easy optional customization with `django-allauth`: only ask for password once
- Set `ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False`

    ```python
    # bookstore_project/settings.py
    # django-allauth config
    ...
    ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False # new
    ```

- Sign up for a testuser account, then check registration email with `docker-compose logs`
    - Note: Later we'll configure this and set up a proper email service.

### Admin

- `django-allauth` adds two new sections: `Accounts` and `Sites`

### Email Only Login

- Lets use `django-allauth`'s awesome [config options](https://django-allauth.readthedocs.io/en/latest/configuration.html) to not require new users to enter a username.
- First, make `username` not required, but set `email` to required.
- Then require `email` to be unique and the authentication method of choice.
- Updated `bookstore_project/settings.py`

    ```python
    # bookstore_project/settings.py
    # django-allauth config
    ...
    ACCOUNT_USERNAME_REQUIRED = False # new
    ACCOUNT_AUTHENTICATION_METHOD = 'email' # new
    ACCOUNT_EMAIL_REQUIRED = True # new
    ACCOUNT_UNIQUE_EMAIL = True # new
    ```

- Create a new testuser2@email.com
- In admin, notice that `django-allauth` automatically populates a username for the new user based on their email before the '@' symbol. This is because the underlying `CustomUser` model still has a `username` field...we haven't deleted it
- This is totally fine, but we should check for an edge-case. What if two users try to sign up with the same email before the '@' symbol?
    - `django-allauth` automatically adds an extra string to the username. Awesome!

## Tests

- `django-allauth` comes with tests built-in, so we only need to test that our project works as expected.
- From our old `tests.py`, there are now 3 errors related to `SignupPageTests` since we've switched to `django-allauth` rather than using our own views, forms, and urls.
- To fix these, change `signup` to `account_signup` (provided by `django-allauth` [source code](https://github.com/pennersr/django-allauth/blob/master/allauth/account/urls.py))
- Then change the location of `signup.html` template to `account/signup.html`
- Remove the test for `CustomUserCreationForm`, since we aren't using it anymore. Also remove the imports for `CustomUserCreationForm` and `SignupPageView`
- Updated `users/tests.py`

    ```python
    # users/tests.py
    from django.contrib.auth import get_user_model
    from django.test import TestCase
    from django.urls import reverse, resolve

    class CustomUserTests(TestCase):
      ...
    class SignupTests(TestCase): # new
      username = 'newuser'
      email = 'newuser@email.com'
      def setUp(self):
        url = reverse('account_signup')
        self.response = self.client.get(url)
      def test_signup_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'account/signup.html')
        self.assertContains(self.response, 'Sign Up')
        self.assertNotContains(
          self.response, 'Hi there! I should not be on the page.')
      def test_signup_form(self):
        new_user = get_user_model().objects.create_user(
          self.username, self.email)
        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertEqual(get_user_model().objects.all()
                        [0].username, self.username)
        self.assertEqual(get_user_model().objects.all()
                        [0].email, self.email)
    ```

## Social Auth

- Goal: Add social auth for GitHub, Gmail
- [List of social authentication provider options](https://github.com/pennersr/django-allauth/tree/master/allauth/socialaccount/providers)

### Update Settings

- Updated `settings.py`

    ```python
    # config/settings.py
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.sites',

        'allauth',
        'allauth.account',
        
        # django-allauth social providers (new)
        'allauth.socialaccount',
        'allauth.socialaccount.providers.github',
        'allauth.socialaccount.providers.google',
        'allauth.socialaccount.providers.reddit',
        'allauth.socialaccount.providers.facebook',
        'allauth.socialaccount.providers.steam',
        
        ...
    ]
    ```

- `docker-compose exec web python manage.py migrate`

## Social OAuth

- Find details for setting up OAuth for each provider at the [documentation](https://django-allauth.readthedocs.io/en/latest/providers.html#github)

### Admin Config

- Go to sites, set the domain name to 127.0.0.1
    - Note: this would obviously be changed to the production homepage when launching to the web
- For each provider...click on *add* for `Social Applications` and fill out the necessary info
    - Don't  forget to add our site to `chosen sites`, otherwise it won't work!

### Github

- [Go here](https://github.com/settings/applications/new) to create a new OAuth application
- Use the *Authorization callback URL* defined in the docs ([link](https://django-allauth.readthedocs.io/en/latest/providers.html))
- Take note of the Client ID and Client Secret

### Login Template

- Updated code for login images

    ```html
    <!-- social authentication -->
    <div id="social-auth">
      <!-- github -->
      <a href="{% provider_login_url 'github' %}">
        <img class="social-auth-icons" alt="Github" src="{% static 'images/github.jpg' %}">
      </a>
      <!-- google -->
      <a href="{% provider_login_url 'google' %}">
        <img class="social-auth-icons" alt="Google" src="{% static 'images/google.jpg' %}">
      </a>
    </div>
    ```