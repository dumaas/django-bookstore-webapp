## Basic Setup

- Django App Initial Config
    - `mkdir books && cd books`
    - `pipenv install django psycopg2-binary`, `pipenv shell`
    - `django-admin startproject bookstore_project .`
    - `python manage.py runserver`
    - `exit` the virtual environment
- Docker Initial Config
    - `touch Dockerfile && touch docker-compose.yml`
        - `Dockerfile` code

            ```docker
            # Pull base image
            FROM python:3.8

            # Set environment variables
            ENV PYTHONDONTWRITEBYTECODE 1
            ENV PYTHONUNBUFFERED 1

            # Set work dir
            WORKDIR /code

            # Install dependencies
            COPY Pipfile Pipfile.lock /code/
            RUN pip install pipenv && pipenv install --system

            # Copy project
            COPY . /code/
            ```

        - `docker-compose.yml` code

            ```docker
            version: '3.8'

            services:
              web:
                build: .
                command: python /code/manage.py runserver 0.0.0.0:8000
                volumes:
                  - .:/code
                ports:
                  - 8000:8000
                depends_on:
                  - db
              db:
                image: postgres:11
                volumes:
                  - postgres_data:/var/lib/postgresql/data/
                environment:
                  - "POSTGRES_HOST_AUTH_METHOD=trust"

            volumes:
              postgres_data:
            ```

            - Note: We're adding a dedicated `volume` for the database so it persists even when the `services` containers are stopped.
    - `docker-compose up -d --build`
- Connect `settings.py` to PostgreSQL

    ```python
    # bookstore_project/settings.py
    DATABASES = {
      'default': {
      'ENGINE': 'django.db.backends.postgresql',
      'NAME': 'postgres',
      'USER': 'postgres',
      'PASSWORD': 'postgres',
      'HOST': 'db',
      'PORT': 5432,
      }
    }
    ```

## 1. Create a `Custom User` Model

- Create a `users` app: `docker-compose exec web python manage.py startapp users`
- Create a `CustomUser` model which extends `AbstractUser`

    ```python
    # users/models.py
    from django.contrib.auth.models import AbstractUser
    from django.db import models

    class CustomUser(AbstractUser):
      pass
    ```

## 2. Update `settings.py`

- Add `users` app to `INSTALLED_APPS`, add `AUTH_USER_MODEL` config

    ```python
    # bookstore_project/settings.py
    INSTALLED_APPS = [
      ...
      # Local
      'users.apps.UsersConfig',
    ]
    ...
    # Custom User Model
    AUTH_USER_MODEL = 'users.CustomUser'
    ```

- Migrate: `docker-compose exec web python manage.py makemigrations users`, then `docker-compose exec web python manage.py migrate`

## 3. Customize `UserCreationForm` and `UserChangeForm`

- `touch users/forms.py`
- Code

    ```python
    # users/forms.py
    from django.contrib.auth import get_user_model
    from django.contrib.auth.forms import UserCreationForm, UserChangeForm

    class CustomUserCreationForm(UserCreationForm):
      class Meta:
        model = get_user_model()
        fields = ('email', 'username',)

    class CustomUserChangeForm(UserChangeForm):
      class Meta:
        model = get_user_model()
        fields = ('email', 'username',)
    ```

## 4. Add the custom user model to `admin.py`

- Extend the existing `UserAdmin` into `CustomUserAdmin` and tell Django to use the new forms, custom user model, and list only the email and username of a user.
    - Note: We could [display more user fields](https://docs.djangoproject.com/en/2.2/ref/contrib/auth/) to `list_display` if we wanted...
    - Code

        ```python
        # users/admin.py
        from django.contrib import admin
        from django.contrib.auth import get_user_model
        from django.contrib.auth.admin import UserAdmin

        from .forms import CustomUserCreationForm, CustomUserChangeForm

        CustomUser = get_user_model()

        class CustomUserAdmin(UserAdmin):
          add_form = CustomUserCreationForm
          form = CustomUserChangeForm
          model = CustomUser
          list_display = ['email', 'username', ]

        admin.site.register(CustomUser, CustomUserAdmin)
        ```

- Confirm the custom user model is working properly by creating a superuser. This command accesses the `CustomUserCreationForm` under the hood.
    - `docker-compoes exec web python manage.py createsuperuser`

## Testing

> Code without tests is broken as designed - Jacob Kaplan-Moss (Django co-founder)

- There are two main types of tests:
    - **Unit tests** — small, fast, and isolated for a specific piece of functionality
        - Django comes with its own [unit testing framework](https://docs.python.org/3.7/library/unittest.html) and Django's [automated testing framework](https://docs.djangoproject.com/en/2.2/topics/testing/). Use these to write LOTS of tests!
    - **Integration tests** — large, slow, used for testing an entire application or a user flow (like payment) that covers multiple screens

## Unit Tests

- Use Django's [TestCase](https://docs.djangoproject.com/en/2.2/topics/testing/tools/#django.test.TestCase) to write unit tests
- Code

    ```python
    # users/tests.py
    from django.contrib.auth import get_user_model
    from django.test import TestCase

    class CustomUserTests(TestCase):
      def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='dumaas',
            email='dumaas@email.com',
            password='testpass123',
        )
        self.assertEqual(user.username, 'dumaas')
        self.assertEqual(user.email, 'dumaas@email.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

      def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username='superadmin',
            email='superadmin@email.com',
            password='testpass123',
        )
        self.assertEqual(admin_user.username, 'superadmin')
        self.assertEqual(admin_user.email, 'superadmin@email.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
    ```

- Run tests: `docker-compose exec web python manage.py test`