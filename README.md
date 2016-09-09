# Sententia
**Sententia - fully-featured voting app in Django.** 

It's a project for my Bachelor's degree so please do request any new features (you can report issues tho). Project is alive on https://sententiaup.pl

### Mandatory system requirements
* PostgreSQL 9.6
* Python 2.7 (Python 3 support is comming)
* git
* Optional: virtualenv

### Requirements
* [django 1.9](https://docs.djangoproject.com/en/1.9/)
* [django-tabbed-admin](https://pypi.python.org/pypi/django-tabbed-admin/1.0.0)
* [django-nested-admin](https://github.com/theatlantic/django-nested-admin)
* [django-admin-sortable](https://pypi.python.org/pypi/django-admin-sortable/)
* [django-compressor](https://django-compressor.readthedocs.io)
* [Psycopg2](https://pypi.python.org/pypi/psycopg2)
* [xlwt](http://xlwt.readthedocs.org/en/latest/)

### Manual
1. Clone repo to your desired directory: ```git clone https://github.com/kamilgregorczyk/sententia.git && cd sententia```
2. Create a virtualenv for the project ```mkvirtualenv sententia```
3. Install the requirements ```pip install -r requirements.txt```
4. Update your database settings in a local settings file ```nano sententia/local.py```
5. Export path to local settings file ```export DJANG_SETTINGS_MODULE=sententia.local```
6. Create tables in your database (migrations) ```./manage.py migrate```
7. Create an account ```./manage.py createsuperuser```
8. Start a server on http://localhost:8000 ```./manage.py runserver```

