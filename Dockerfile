FROM python:3

# debian packages: GeoDjango dependencies
RUN apt-get update && \
    apt-get install -y binutils libproj-dev gdal-bin && \
    rm -rf /var/lib/apt/lists/*

# python packages
COPY ./requirements /usr/src/app/requirements
RUN pip install --no-cache-dir -r /usr/src/app/requirements/production.txt

# django apps & manage
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY ./config /usr/src/app/config
COPY ./landing /usr/src/app/landing
COPY ./notifications /usr/src/app/notifications
COPY ./manage.py /usr/src/app/manage.py
COPY ./pairup /usr/src/app/pairup
COPY ./chat /usr/src/app/chat
COPY ./user_profile /usr/src/app/user_profile
COPY ./.env /usr/src/app/.env

ENV DJANGO_SETTINGS_MODULE=config.settings.production
ENV DATABASE_URL postgis://$DBUSER:$DBPASSWORD@$DBHOST:$DBPORT/$DBNAME
# ENV DJANGO_SECRET_KEY=VGWuawqwFvVJmnhhu0ITPmPkn1WznuqZ4mDU5jrBNXqkY3mdrfTAimC7wzCpj7PG
ENV DJANGO_AWS_ACCESS_KEY_ID=0
ENV DJANGO_AWS_SECRET_ACCESS_KEY=0
ENV DJANGO_AWS_STORAGE_BUCKET_NAME=0
ENV DJANGO_ADMIN_URL=
ENV MAILGUN_API_KEY=
ENV MAILGUN_DOMAIN=
ENV DJANGO_DEBUG True
ENV DJANGO_SENTRY_DSN https://6d9758b0c96a433188228cc2b38b0571:6a15f1539e1c42eb8e1ad7d773f27a13@sentry.io/668679
#ENV REDIS_URL redis://h:pf954c886918ca88905dcf8fef4546bd9dbc2738d5895b12bc36ed2d058c387ec@ec2-34-201-226-230.compute-1.amazonaws.com:7719
#ENV REDIS_HOST redis://h:pf954c886918ca88905dcf8fef4546bd9dbc2738d5895b12bc36ed2d058c387ec@ec2-34-201-226-230.compute-1.amazonaws.com:7719

RUN ./manage.py collectstatic --no-input
# WORKDIR /app
# Heroku doesn't like EXPOSE
# EXPOSE 8000
RUN adduser --disabled-password myuser
USER myuser

#CMD gunicorn config.wsgi:application --bind=0:$PORT --access-logfile=- --error-logfile=-
# CMD daphne --bind=0:$PORT config.asgi:application -v2
# CMD daphne -e ssl:443:privateKey=key.pem:certKey=crt.pem config.asgi:application
CMD daphne config.asgi:application --port $PORT --bind 0.0.0.0 -v2
