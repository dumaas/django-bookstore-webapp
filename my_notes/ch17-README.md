## How to Choose a Hosting Provider

### PaaS vs IaaS

- Platform-as-a-Service (PaaS) — Opinionated, handles much of the initial configuration and scaling for you ([Heroku](https://www.heroku.com/), [PythonAnywhere](https://www.pythonanywhere.com/details/django_hosting), [Dokku](http://dokku.viewdocs.io/dokku/))
    - Costs more money up front, but saves a lot of developer time, handles security updates automatically, and can scale quickly
- Infrastructure-as-a-Service (IaaS) — Provides total flexibility, is usually cheaper, but requires a lot of knowledge and effort to set up properly ([DigitalOcean](https://www.digitalocean.com/), [Linode](https://www.linode.com/), [Amazon EC2](https://aws.amazon.com/ec2/), [Google Compute Engine](https://cloud.google.com/compute/))
- For this project we'll use PaaS since it's simpler. We'll be going with Heroku!

### [WhiteNoise](https://github.com/evansd/whitenoise)

- Django uses the staticfiles app for serving files locally
- For production, you can run [collectstatic](https://docs.djangoproject.com/en/2.2/ref/contrib/staticfiles/#collectstatic) into a directory (specified by [STATIC_ROOT](https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-STATIC_ROOT)) which can then be served either on the same server, a different server, or a dedicated cloud service/CDN by updating [STATICFILES_STORAGE](https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-STATICFILES_STORAGE)
- Don't optimize by going straight for a CDN...the default option of serving from your server's filesystem scales to a pretty big size. If you go this route, check out [django-storages](https://github.com/jschneier/django-storages)
- First `pipenv install whitenoise`, then stop Docker
- Update `[settings.py](http://settings.py)` to use whitenoise locally as well!

    ```python
    # bookstore_project/settings.py
    INSTALLED_APPS = [
      'django.contrib.admin',
      'django.contrib.auth',
      'django.contrib.contenttypes',
      'django.contrib.sessions',
      'django.contrib.messages',
      'whitenoise.runserver_nostatic', # new
      'django.contrib.staticfiles',
      'django.contrib.sites',
      ...
    ]
    MIDDLEWARE = [
      'django.middleware.cache.UpdateCacheMiddleware',
      'django.middleware.security.SecurityMiddleware',
      'whitenoise.middleware.WhiteNoiseMiddleware', # new
      ...
    ]
    ```

- Then rebuild Docker
- Run `collectstatic` one more time

### [Gunicorn](https://gunicorn.org/) (or [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/))

- When we first ran `startproject`, the `[wsgi.py](http://wsgi.py)` file was created with a default [WSGI](https://wsgi.readthedocs.io/en/latest/)
    - This specifies how the web app communicates with the web server
- `pipenv install gunicorn`, turn off Docker
- Update `docker-compose.yml` and `docker-compose-prod.yml` to use Gunicorn

    ```docker
    # command: python /code/manage.py runserver 0.0.0.0:8000
    command: gunicorn bookstore_project.wsgi -b 0.0.0.0:8000 # new
    ```

- Rebuild Docker

### [dj-database-url](https://github.com/kennethreitz/dj-database-url)

- Database information is given to Heroku via `DATABASE_URL`. dj-database-url allows us to parse the `DATABASE_URL` environment variable and auto-convert it to the right config format
- `pipenv install dj-database-url`, then stop Docker
- Updated `settings.py`

    ```python
    # bookstore_project/settings.py
    # Heroku
    import dj_database_url
    db_from_env = dj_database_url.config(conn_max_age=500)
    DATABASES['default'].update(db_from_env)
    ```

- Rebuild Docker

## Adding a Production-Ready Web Server

### [Heroku](https://www.heroku.com)

- Create an account, then [install Heroku's CLI](https://devcenter.heroku.com/articles/getting-started-with-python#set-up) to deploy from the command line
    - Log in on the CLI with `heroku login`

### Deploying with Docker

- Rather than deploying on Heroku the traditional way, [we'll deploy using Docker containers](https://devcenter.heroku.com/categories/deploying-with-docker). This makes switching to a different hosting provider MUCH easier later on.

### [Heroku.yml](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml)

- Rather than using a `Procfile`, we'll use a `heroku.yml` file to deploy
- Here you can [configure](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml#heroku-yml-overview) `setup`, `build`, `release`, and `run`
    - In `setup`, we'll be relying on the free `[heroku-postgresql](https://elements.heroku.com/addons/heroku-postgresql)` tier
    - In `build`, we'll specify how the `Dockerfile` should be built. This relies on our current `Dockerfile` in the root dir.
    - In `release`, we can run tasks before each new release is deployed. For example, we can make sure `collectstatic` is run on every deploy automatically.
    - In `run`, we'll specify which process to actually run the application. This is where we'll specify to use `Gunicorn` for the web server.
- Code for `heroku.yml`

    ```docker
    setup:
      addons:
      - plan: heroku-postgresql
    build:
      docker:
        web: Dockerfile
    release:
      image: web
      command:
        - python manage.py collectstatic --noinput
    run:
      web: gunicorn bookstore_project.wsgi
    ```

- Finally, commit new changes to git

### Heroku Deployment

- Create heroku app with `heroku create APPNAME`
- My app is at [https://django-bookstore-webapp.herokuapp.com/](https://django-bookstore-webapp.herokuapp.com/)
- Click on the app on the Heroku dashboard, go to settings
- Click "Reveal Config Vars", then add environment variables for `ENVIRONMENT` to "production", the `SECRET_KEY`, and `DEBUG` to "False" from `docker-compose-prod.yml`
- Now set the [stack](https://devcenter.heroku.com/articles/stack) to use our Docker containers instead of Heroku's default buildpack
    - `heroku stack:set container -a APPNAME`
- Finally, specify the hosted PostgreSQL database we want. In our case, we'll use the free `hobby-dev` tier
    - `heroku addons:create heroku-postgresql:hobby-dev -a APPNAME`
    - Note: the `dj-database-url` settings will automatically find and use this `DATABASE_URL` for us
- We're ready to deploy!! Create a [Heroku remote](https://devcenter.heroku.com/articles/git#creating-a-heroku-remote) — a version of our code that lives on the Heroku server.
    - `heroku git:remote -a APPNAME`
    - `git push heroku main`
- Since the code is only a mirror of our local code, the production site has its own (empty) database.
- To run commands, add `heroku run` to normal commands.
- We should `migrate` the initial database and then `createsuperuser`
    - `heroku run python manage.py migrate`
    - `heroku run python manage.py createsuperuser`
- Open the app with `heroku open -a APPNAME`, or from the Heroku dashboard
- For some reason the app still isn't working properly...

### [SECURE_PROXY_SSL_HEADER](https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-SECURE_PROXY_SSL_HEADER)

- Heroku uses proxies, so we must find the proper header and update this accordingly.
- Update `[settings.py](http://settings.py)` to trust Heroku

    ```python
    # bookstore_project/settings.py
    # production
    if ENVIRONMENT == 'production':
      SECURE_BROWSER_XSS_FILTER = True
      X_FRAME_OPTIONS = 'DENY'
      SECURE_SSL_REDIRECT = True
      SECURE_HSTS_SECONDS = 3600
      SECURE_HSTS_INCLUDE_SUBDOMAINS = True
      SECURE_HSTS_PRELOAD = True
      SECURE_CONTENT_TYPE_NOSNIFF = True
      SESSION_COOKIE_SECURE = True
      CSRF_COOKIE_SECURE = True
      SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') # new
    ```

- Add the heroku URL to `ALLOWED_HOSTS`

    ```python
    # bookstore_project/settings.py
    ALLOWED_HOSTS = ['APPNAME.herokuapp.com', 'localhost', '127.0.0.1']
    ```

- Commit changes to git and push updated code to Heroku

### Heroku Logs

- Deployment errors are inevitable... run `heroku logs --tail` to see error and info logs to debug issues

### Heroku [Add-ons](https://elements.heroku.com/addons/)

- [Memcachier](https://elements.heroku.com/addons/memcachier) adds caching
- [Daily backups](https://devcenter.heroku.com/articles/heroku-postgres-backups#scheduling-backups) are pretty essential
- You can use custom domains and ensure SSL, but you'll need to be on a [Heroku paid tier](https://devcenter.heroku.com/articles/understanding-ssl-on-heroku)

### [PonyCheckup](https://www.ponycheckup.com/)

- This is a popular way to test Django deployments