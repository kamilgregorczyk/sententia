# Sententia
**Sententia - fully-featured voting app in Django.** 

It's a project for my Bachelor's degree so please do request any new features (you can report issues tho).

### Mandatory system requirements
* Docker
* Docker compose

### Requirements
* [django 1.9](https://docs.djangoproject.com/en/1.9/)
* [django-tabbed-admin](https://pypi.python.org/pypi/django-tabbed-admin/1.0.0)
* [django-nested-admin](https://github.com/theatlantic/django-nested-admin)
* [django-admin-sortable](https://pypi.python.org/pypi/django-admin-sortable/)
* [django-compressor](https://django-compressor.readthedocs.io)
* [Psycopg2](https://pypi.python.org/pypi/psycopg2)
* [xlwt](http://xlwt.readthedocs.org/en/latest/)

### Manual
1. Create docker volume ```docker volume create pgdata```
2. Run all services ```docker-compose up```
3. Go to http://localhost (if you see your own http server then change ngxin port)
