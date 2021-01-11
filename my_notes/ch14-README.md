## Search Results Page

- Search functionality comes in two parts: a form to pass a user search query and a results page that performs a filter based on that query
- Determining "the right" type of filter is where search is interesting and difficult.
- URL, views, template
    - Code for `urls.py`

        ```python
        # books/urls.py
        from django.urls import path

        from .views import (
            BookListView,
            BookDetailView,
            SearchResultsListView,
        )

        urlpatterns = [
            path('', BookListView.as_view(), name='book_list'),
            path('<uuid:pk>', BookDetailView.as_view(), name='book_detail'),
            path('search/', SearchResultsListView.as_view(), name='search_results'),
        ]
        ```

    - Code for `views.py`

        ```python
        # books/views.py
        ...
        class SearchResultsListView(ListView):
          model = Book
          context_object_name = 'book_list'
          template_name = 'books/search_results.html'
        ```

    - Code for `search_results.html`

        ```html
        <!-- templates/books/search_results.html -->
        {% extends '_base.html' %}

        {% block title %}Search{% endblock title %}

        {% block content %}
        <h1>Search Results</h1>
        {% for book in book_list %}
          <div>
            <h3><a href="{{ book.get_absolute_url }}">{{ book.title }}</a></h3>
            <p>Author: {{ book.author }}</p>
            <p>Price: {{ book.price }}</p>
          </div>
        {% endfor %}
        {% endblock content %}
        ```

## Basic Filtering

- [QuerySet's](https://docs.djangoproject.com/en/2.2/topics/db/queries/#retrieving-objects) are used in Django to filter results from a database model
- You can use a [manager](https://docs.djangoproject.com/en/2.2/topics/db/managers/#django.db.models.Manager) on the model itself to customize a queryset, but that's a little more complicated.
- Do a basic queryset override in `[views.py](http://views.py)` to restrict search to only those with "beginners" in the name!

    ```python
    # books/views.py
    ...
    class SearchResultsListView(ListView):
      model = Book
      context_object_name = 'book_list'
      template_name = 'books/search_results.html'
      queryset = Book.objects.filter(title__icontains='beginners')
    ```

- The [built-in queryset methods](https://docs.djangoproject.com/en/2.2/topics/db/queries/#other-queryset-methods) are great for basic filtering — `filter()`, `all()`, `get()`, `exclude()`, etc
- The [QuerySet API](https://docs.djangoproject.com/en/2.2/ref/models/querysets/#queryset-api) is very robust and can be useful for more in-depth search forms

### Q Objects

- `filter()` is powerful, especially if you [chain filters](https://docs.djangoproject.com/en/2.2/topics/db/queries/#chaining-filters) together to search for all titles with "beginners" and "django" (for example)...but most of the time you'll want complex lookups that can use OR, not just AND.
- This is where [Q Objects](https://docs.djangoproject.com/en/2.2/topics/db/queries/#complex-lookups-with-q-objects) come in!
- Example to filter a result with titles EITHER 'beginners' OR 'api'

    ```python
    # books/views.py
    from django.db.models import Q # new
    ...
    def get_queryset(self):
        return Book.objects.filter(
            Q(title__icontains='beginners') | Q(title__icontains='api')
        )
    ```

### Forms

- Where does the form data actually go and how do we handle it once it's there?
- Security concerns for letting users submit data to the site???
- Forms can either be sent with `GET` or `POST` methods
    - `POST` — bundles form data, encodes it for transmission, sends it to the server, and receives a response. Any request that changes the state of the database (creates, edits, deletes, etc) should use `POST`
    - `GET` — bundles data into a string that's added to the destination URl. This should only be used for requests that don't affect the state of the application (like a search where nothing in the database changes)
    - For more info, Moz has good guides on [sending form data](https://developer.mozilla.org/en-US/docs/Learn/HTML/Forms/Sending_and_retrieving_form_data) and [form data validation](https://developer.mozilla.org/en-US/docs/Learn/HTML/Forms/Form_validation)

### Search Form

- Updated `home.html`

    ```html
    <!-- templates/home.html -->
    {% block title %}Home{% endblock title %}

    {% block content %}
    <h1>Homepage</h1>
    <form
      class="form-inline mt-2 mt-md-0"
      action="{% url 'search_results' %}"
      method="get">
      <input
        name="q"
        class="form-control mr-sm-2"
        type="text"
        placeholder="Search"
        aria-label="Search">
    </form>
    {% endblock content %}
    ```

- Note: the results haven't changed...we need to integrate the new search form with our views!
- Updated `views.py`

    ```python
    # books/views.py
    ...
    class SearchResultsListView(ListView):
      model = Book
      context_object_name = 'book_list'
      template_name = 'books/search_results.html'

      def get_queryset(self):
        query = self.request.GET.get('q')
        return Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
    ```