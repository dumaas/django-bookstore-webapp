## What are [Environment Variables](https://en.wikipedia.org/wiki/Environment_variable)?

- An extremely important part of [12 Factor App Design](https://12factor.net/), allowing for better levels of security and simpler local/production configs
- Currently [django-environ](https://github.com/joke2k/django-environ) is the best practice for a non-Docker environment, but it's possible to add environment variables directly in Docker with our `docker-compose.yml`

### .env files

- It's possible to use .env files to store environment variables and reference them in a `docker-compose.yml` file
- This is nice because you can choose to selectively ignore `.env` files in the `.gitignore` file
- In practice, chaining together multiple .env files is too complicated and not recommended for a big project. Plugging the variables into `docker-compose.yml` is best!

### [SECRET_KEY](https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-SECRET_KEY)

- To add to `docker-compose.yml`, follow these steps:
    1. Add the values to `docker-compose.yml`
    2. Replace the hardcoded `bookstore_project/settings.py` value with the environment variable
- Updated `docker-compose.yml`
    - NOTE: If your secret key has a $, type it into the file as $$, otherwise it won't work...

    ```docker
    version: '3.8'

    services:
      web:
        build: .
        command: python /code/manage.py runserver 0.0.0.0:8000
        environment:
          - SECRET_KEY=dib1o&f(0kupe2)-u*p*@kv30_!@vrdf1%%(k%i&w2q$*75pvn
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

- Updated `bookstore_project/settings.py`

    ```python
    # bookstore_project/settings.py
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ```

- Finally, stop and restart the Docker containers. Since they're designed to be stateless, the web app will temporarily break after changing environment variables.

### [DEBUG](https://docs.djangoproject.com/en/2.2/ref/settings/#debug)

- Django sets this to `True` by default for local production, but should be set to `False` for deployment
- Eventually we'll use a `docker-compose-prod.yml` file with production-only configs...but for not keep using `docker-compose.yml`
- Updated `docker-compose.yml`
    - NOTE: If your secret key has a $, type it into the file as $$, otherwise it won't work...

    ```docker
    version: '3.8'

    services:
      web:
        build: .
        command: python /code/manage.py runserver 0.0.0.0:8000
        environment:
          - SECRET_KEY=dib1o&f(0kupe2)-u*p*@kv30_!@vrdf1%%(k%i&w2q$*75pvn
          - DEBUG=True  
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

- Updated `bookstore_project/settings.py`

    ```python
    # bookstore_project/settings.py
    DEBUG = os.environ.get('DEBUG')
    ```

### Databases

- It's possible (and recommended) to have multiple levels of users and permissions in your PostgreSQL database.
- We won't do it here, but using environment variables to do this is a good idea too!