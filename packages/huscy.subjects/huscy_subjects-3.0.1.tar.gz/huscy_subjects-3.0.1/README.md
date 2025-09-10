huscy.subjects
======

![PyPi Version](https://img.shields.io/pypi/v/huscy-subjects.svg)
![PyPi Status](https://img.shields.io/pypi/status/huscy-subjects)
![PyPI Downloads](https://img.shields.io/pypi/dm/huscy-subjects)
![PyPI License](https://img.shields.io/pypi/l/huscy-subjects?color=yellow)
![Python Versions](https://img.shields.io/pypi/pyversions/huscy-subjects.svg)
![Django Versions](https://img.shields.io/pypi/djversions/huscy-subjects)



Requirements
------

- Python 3.8+
- A supported version of Django

Tox tests on Django versions 4.2, 5.0 and 5.1.



Installation
------

To install `husy.subjects` simply run:

    pip install huscy.subjects

Add `huscy.subjects` and further required apps to `INSTALLED_APPS` in your `settings.py`:

```python
INSTALLED_APPS = (
	...
	'django_countries',
	'guardian',
	'phonenumber_field',
	'rest_framework',

	'huscy.subjects',
)
```

Hook the urls from `huscy.subjects` into your `urls.py`:

```python
urlpatterns = [
	...
	path('api/', include('huscy.subjects.urls')),
]
```

Create `huscy.subjects` database tables by running:

    python manage.py migrate



Configuration
------

There are some settings to configure the service. These settings have be added to `settings.py`.


| Name | Default value | Description |
| -------- | -------- | -------- |
| HUSCY_SUBJECTS_AGE_OF_MAJORITY | 18 | Specifies the age of majority. |
| HUSCY_SUBJECTS_SUBJECT_VIEWSET_MAX_RESULT_COUNT | 500 | Specifies the maximum number of subjects returned by the queryset in the SubjectViewSet. |



Development
------

Install PostgreSQL and create a database user called `huscy` and a database called `huscy`.

    sudo -u postgres createdb huscy
    sudo -u postgres createuser -d huscy
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE huscy TO huscy;"
    sudo -u postgres psql -c "ALTER USER huscy WITH PASSWORD '123';"

Check out the repository and start your virtual environment (if necessary).

Install dependencies:

    make install

Create database tables:

    make migrate

Run tests to see if everything works fine:

    make test
