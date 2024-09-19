#!/bin/bash

while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
done


# Wait for Elasticsearch to be ready
sleep 30

# Run migrations
echo "Starting Django migrations.."
python manage.py migrate

# Collect static
echo "Collect Static.."
python manage.py collectstatic --no-input

# Check if a superuser with the given username exists
if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi

# Start uWSGI server
uwsgi --strict --ini uwsgi.ini