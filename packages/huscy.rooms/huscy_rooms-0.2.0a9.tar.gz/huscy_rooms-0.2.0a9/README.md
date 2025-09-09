huscy.rooms
======

![PyPi Version](https://img.shields.io/pypi/v/huscy-rooms.svg)
![PyPi Status](https://img.shields.io/pypi/status/huscy-rooms)
![PyPI Downloads](https://img.shields.io/pypi/dm/huscy-rooms)
![PyPI License](https://img.shields.io/pypi/l/huscy-rooms?color=yellow)
![Python Versions](https://img.shields.io/pypi/pyversions/huscy-rooms.svg)
![Django Versions](https://img.shields.io/pypi/djversions/huscy-rooms)



Requirements
------

- Python 3.8+
- A supported version of Django

Tox tests on Django versions 4.2, 5.0 and 5.1.



Installation
------

To install `husy.rooms` simply run:
```
pip install huscy.rooms
```


Configuration
------

We need to hook `huscy.rooms` into our project.

1. Add `huscy.rooms` into your `INSTALLED_APPS` at settings module:

```python
INSTALLED_APPS = (
	...
	'huscy.rooms',
)
```

2. Create `huscy.rooms` database tables by running:

```
python manage.py migrate
```


Development
------

After checking out the repository you should run

```
make install
```

to install all development and test requirements and

```
make migrate
```

to create the database tables.
We assume you have a running postgres database with a user `huscy` and a database also called `huscy`.
You can easily create them by running

```
sudo -u postgres createuser -d huscy
sudo -u postgres psql -c "ALTER USER huscy WITH PASSWORD '123'"
sudo -u postgres createdb huscy
```
