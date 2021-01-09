### Custom Confirmation Emails

- Create new user, check sign up email with `docker-compose logs`
- To customize the email, find the existig templates in the [django-allauth source code](https://github.com/pennersr/django-allauth)
    - There are two files being used to make the email: `email_confirmation_subject.txt` and `email_confirmation_message.txt`
    - To override these files, recreate the same structure django-allauth uses by creating a `templates/account/email/` directory and adding our personalized versions there
- Update the subject line — `email_confirmation_subject.txt`
    - Default

        ```
        {% load i18n %}
        {% autoescape off %}
        {% blocktrans %}Please Confirm Your E-mail Address{% endblocktrans %}
        {% endautoescape %}
        ```

    - New

        ```
        {% load i18n %}
        {% autoescape off %}
        {% blocktrans %}Confirm Your Sign Up{% endblocktrans %}
        {% endautoescape %}
        ```

- Update the subject line — `email_confirmation_message.txt`
    - Default

        ```
        {% load account %}{% user_display user as user_display %}{% load i18n %}
        {% autoescape off %}{% blocktrans with site_name=current_site.name\
        site_domain=current_site.domain %}Hello from {{ site_name }}!

        You're receiving this e-mail because user {{ user_display }} has given yours\
        as an e-mail address to connect their account.

        To confirm this is correct, go to {{ activate_url }}
        {% endblocktrans %}{% endautoescape %}
        {% blocktrans with site_name=current_site.name site_domain=current_site.\
        domain %}Thank you from {{ site_name }}!
        {{ site_domain }}{% endblocktrans %}
        ```

    - New (first update the site name in admin)

        ```
        {% load account %}{% user_display user as user_display %}{% load i18n %}{% autoescape off %}
        {% blocktrans with site_name=current_site.name site_domain=current_site.domain %}\
        Hello from {{ site_name }}!

        You're receiving this e-mail because user {{ user_display }} has given yours\
        as an e-mail address to connect their account.

        To confirm this is correct, go to {{ activate_url }}
        {% endblocktrans %}{% endautoescape %}
        {% blocktrans with site_name=current_site.name site_domain=current_site.domain %}
        Thank you from {{ site_name }}!
        {{ site_domain }}{% endblocktrans %}
        ```

- Change `DEFAULT_FROM_EMAIL` in `settings.py`

    ```python
    # bookstore_project/settings.py
    DEFAULT_FROM_EMAIL = 'admin@djangobookstore.com'
    ```

- Then log out, and create a new user to see the new email message

### Email Confirmation Page

- If you click on the provided link for confirming the email (from the message in `docker-compose logs`), it looks pretty lame lol. Let's make it better!
- Create `templates/account/email_confirm.html`

    ```html
    <!-- templates/account/email_confirm.html -->
    {% extends '_base.html' %}
    {% load i18n %}
    {% load account %}

    {% block head_title %}{% trans "Confirm E-mail Address" %}{% endblock %}

    {% block content %}
      <h1>{% trans "Confirm E-mail Address" %}</h1>
      {% if confirmation %}
        {% user_display confirmation.email_address.user as user_display %}
        <p>{% blocktrans with confirmation.email_address.email as email %}Please confirm
    that <a href="mailto:{{ email }}">{{ email }}</a> is an e-mail address for user
    {{ user_display }}.{% endblocktrans %}</p>
        <form method="post" action="{% url 'account_confirm_email' confirmation.key %}">
    {% csrf_token %}
          <button class="btn btn-primary" type="submit">{% trans 'Confirm' %}</button>
        </form>
      {% else %}
        {% url 'account_email' as email_url %}
        <p>{% blocktrans %}This e-mail confirmation link expired or is invalid. Please
        <a href="{{ email_url }}">issue a new e-mail confirmation request</a>.{% endblocktrans %}</p>
      {% endif %}
    {% endblock %}
    ```