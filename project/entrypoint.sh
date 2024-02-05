#!/bin/sh

# python manage.py flush --no-input
#pyhton manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input --clear

exec "$@"
