### [Social Engineering](https://en.wikipedia.org/wiki/Social_engineering_(security))

- [Phishing](https://en.wikipedia.org/wiki/Phishing) is the most likely way for hackers to get into an organization
- As a rule of thumb, only add permissions as needed! Don't default to SU for everyone.

### Django Updates

- It's always better and more secure to stay up to date.
- Django's [deprecation warnings](https://docs.djangoproject.com/en/2.2/howto/upgrade-version/) tell you what in your code might be depreciated after updating

### Deployment Checklist

- Django's [deployment checklist](https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/) is great for getting all of the security settings right
    - OR run `python manage.py check --deploy`
    - This uses [Django's system check framework](https://docs.djangoproject.com/en/2.2/topics/checks/), which can be used to customize similar commands in mature projects

## Local vs Production

- Add an `ENVIRONMENT` setting in `settings.py`, right below `BASE_DIR`

    ```python
    # bookstore_project/settings.py
    ENVIRONMENT = os.environ.get('ENVIRONMENT', default='development')
    ```

- Add an `ENVIRONMENT` variable in `docker-compose.yml`

    ```docker
    version: '3.8'
    services:
      web:
        build: .
        command: python /code/manage.py runserver 0.0.0.0:8000
        environment:
          - ENVIRONMENT=development
    ...
    ```

- Create a dedicated `docker-compose-prod.yml` JUST for production settings (remove volumes), change `ENVIRONMENT` to production

    ```docker
    version: '3.8'

    services:
      web:
        build: .
        command: python /code/manage.py runserver 0.0.0.0:8000
        environment:
          - ENVIRONMENT=production
          - SECRET_KEY=dib1o&f(0kupe2)-u*p*@kv30_!@vrdf1%%(k%i&w2q$$*75pvn
          - DEBUG=True
          - SENDGRID_API_KEY=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
          - STRIPE_TEST_PUBLISHABLE_KEY=pk_test_51I8WIHGjtkNqnDMcvQ0MvuWqgyTd7Opl43qqB3nl57WXAAPmTq4caga3fWUxM30rqtcURwzAModZnGaMu5pKBBU600naGOt0TY
          - STRIPE_TEST_SECRET_KEY=sk_test_51I8WIHGjtkNqnDMcADV590czOheo9XiUHHjXxaGPL5tjuxnwNLC4bm2Cj9N4hYoitxkHw6HdHw1K4gbIfzGdjWbR00kSIaluoz
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
    ```

### [Debug](https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-DEBUG)

- change `DEBUG=False`

### `[ALLOWED_HOSTS](https://docs.djangoproject.com/en/2.2/ref/settings/#allowed-hosts)`

- Update `[settings.py](http://settings.py)`

    ```python
    # bookstore_project/settings.py
    ALLOWED_HOSTS = ['.herokuapp.com', 'localhost', '127.0.0.1']
    ```

- To confirm this, restart Docker with `-f` to specify an [alternate compose file](https://docs.docker.com/compose/reference/overview/)
- Then `migrate`
- Run the `--deploy` check again...only a few more to go!

## Web Security

- Overview on web security from [Django' security page](https://docs.djangoproject.com/en/2.2/topics/security/)

### [SQL injection](https://en.wikipedia.org/wiki/SQL_injection)

- When someone injects SQL commands into the database, they can delete everything!
- [This](https://www.xkcd.com/327/) is what can happen...
- [This cheat sheet](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.md) is great and has suggestions for this

### [XSS (Cross Site Scripting)](https://en.wikipedia.org/wiki/Cross-site_scripting)

- When someone adds their own javascript to your website
- [This cheat sheet is useful!](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.md)
- Django does a lot for this, but we still need to set `SECURE_BROWSER_XSS_FILTER=True`
- Updated `settings.py`

    ```python
    # bookstore_project/settings.py
    # production
    if ENVIRONMENT == 'production':
      SECURE_BROWSER_XSS_FILTER = True # new
    ```

- Restart docker and run `check --deploy` again! Onward we go!

### [Cross-Site Request Forgery (CSRF)](https://en.wikipedia.org/wiki/Cross-site_request_forgery)

- Allows hackers to get access to sites a user is logged into
- [This cheatsheet is great!](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md)
- Whenever you have a form on your site, USE A `CSRF_TOKEN`

### [Clickjacking](https://en.wikipedia.org/wiki/Clickjacking) Protection

- When a hacker tricks a user into clicking on a hidden frame
- [Useful cheatsheet!](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Clickjacking_Defense_Cheat_Sheet.md)
- Updated `settings.py`

    ```python
    # bookstore_project/settings.py
    # production
    if ENVIRONMENT == 'production':
      SECURE_BROWSER_XSS_FILTER = True
      X_FRAME_OPTIONS = 'DENY' # new
    ```

- Reboot the server, then `check --deploy`

### [HTTPS](https://en.wikipedia.org/wiki/HTTPS)/[SSL](https://en.wikipedia.org/wiki/Transport_Layer_Security)

- Without HTTPS, hackers can listen to incoming/outgoing traffic for data
- Updated `settings.py`

    ```python
    # bookstore_project/settings.py
    # production
    if ENVIRONMENT == 'production':
      SECURE_BROWSER_XSS_FILTER = True
      X_FRAME_OPTIONS = 'DENY'
      SECURE_SSL_REDIRECT = True # new
    ```

### [HTTP Strict Transport Security (HSTS)](https://en.wikipedia.org/wiki/HTTP_Strict_Transport_Security)

- Allows the server to enforce that web browsers should ONLY interact via HTTPS
- Updated `settings.py`

    ```python
    # bookstore_project/settings.py
    # production
    if ENVIRONMENT == 'production':
      SECURE_BROWSER_XSS_FILTER = True
      X_FRAME_OPTIONS = 'DENY'
      SECURE_SSL_REDIRECT = True
      SECURE_HSTS_SECONDS = 3600 # new
      SECURE_HSTS_INCLUDE_SUBDOMAINS = True # new
      SECURE_HSTS_PRELOAD = True # new
      SECURE_CONTENT_TYPE_NOSNIFF = True # new
    ```

### Secure [Cookies](https://en.wikipedia.org/wiki/HTTP_cookie)

- Cookies should be forced over HTTPS!
- Updated `settings.py`

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
      SESSION_COOKIE_SECURE = True # new
      CSRF_COOKIE_SECURE = True # new
    ```

- Rebuild Docker, then `check --deploy`

## Admin Hardening

- By default, Django does NOT secure the Admin very well.
1. Change the admin URL to ANYTHING else
    - Updated `urls.py`

        ```python
        # bookstore_project/urls.py
        from django.conf import settings
        from django.conf.urls.static import static
        from django.contrib import admin
        from django.urls import path, include
        urlpatterns = [
          # Django admin
          path('anything-but-admin/', admin.site.urls), # new
          # User management
          path('accounts/', include('allauth.urls')),
          # Local apps
          path('', include('pages.urls')),
          path('books/', include('books.urls')),
        ]
        if settings.DEBUG:
          urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        ```

    - A fun package is [django-admin-honeypot](https://github.com/dmpayton/django-admin-honeypot), which sends you the IP address of anyone trying to access the default /admin/ url. You can then block their IP from the site!
    - You can alsoe use [django-two-factor-auth](https://github.com/Bouke/django-two-factor-auth) to add two-factor authentication to admin for even more protection