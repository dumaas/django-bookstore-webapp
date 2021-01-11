# Bookstore App
## [Initial Setup](my_notes/ch03-README.md)
- Initializing the Django app
- Docker initial config
- PostgreSQL initial config
- Create a CustomUser Model
- Add unit tests

## [Pages App](my_notes/ch04-README.md)
- Initializing Pages app with templates, urls, and views
- Testing homepage templates, html, resolve
- Simplify testing with setUp method

## [User Registration](my_notes/ch05-README.md)
- Add log-in and log-out functionality
- Learn how to search for magic in the [Django source code](https://github.com/django/django)
- Add sign up functionality (URLs, views, templates, etc)
- Test new signup status code, templates used, etc.

## [Static Assets](my_notes/ch06-README.md)
- Create the staticfiles app
- Add custom CSS, images, and JavaScript
- Add Bootstrap
- Create the about page
- Add [django-crispy-forms](https://github.com/django-crispy-forms/django-crispy-forms)
- Add about page tests

## [Advanced User Registration](my_notes/ch07-README.md)
- Setup [django-allauth](https://github.com/pennersr/django-allauth)
- Test new signup features
- Add social auth (Github and Google)

## [Environment Variables](my_notes/ch08-README.md)
- Why I don't use .env files
- Add SECRET_KEY, DEBUG to docker-compose.yml
- Info on database environment variables

## [Email](my_notes/ch09-README.md)
- Custom confirmation emails
- Edit email confirmation page
- Add SendGrid API integration

## [Books App](my_notes/ch10-README.md)
- Create models, urls, views, templates for Books app
- Setup individual book pages
- Switch from primary keys to UUIDs
- Add books app to navbar
- Add testing for books app

## [Reviews App](my_notes/ch11-README.md)
- Add one-to-many relationship for reviews model
- Integrate reviews in admin model
- Update book template to display reviews
- Test review functionality

## [File / Image Upload](my_notes/ch12-README.md)
- Using [Pillow](https://python-pillow.org/)
- New Models, Admin, Template setup

## [Permissions](my_notes/ch13-README.md)
- Restrict books page to logged-in users
- Add custom permissions for viewing individual book pages
- Add testing for new permissions
