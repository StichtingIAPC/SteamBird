FROM python:3.7-alpine

RUN mkdir /project
WORKDIR /project

RUN apk add --update alpine-sdk linux-headers mailcap postgresql-dev    &&\
    pip3 install https://projects.unbit.it/downloads/uwsgi-lts.tar.gz   &&\
    pip3 install pipenv django-uwsgi                                    &&\
    find / -type d -name __pycache__ -exec rm -r {} +                   &&\
    rm -rf /usr/lib/python*/ensurepip                                   &&\
    rm -rf /usr/lib/python*/turtledemo                                  &&\
    rm -rf /usr/lib/python*/idlelib                                     &&\
    rm -f /usr/lib/python*/turtle.py                                    &&\
    rm -f /usr/lib/python*/webbrowser.py                                &&\
    rm -f /usr/lib/python*/doctest.py                                   &&\
    rm -f /usr/lib/python*/pydoc.py                                     &&\
    rm -rf /root/.cache /var/cache

COPY Pipfile /project/
COPY Pipfile.lock /project/

RUN pipenv install --system --deploy

COPY . /project/
COPY entrypoint.sh /usr/local/bin/

ENV DEBUG=False

RUN python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["entrypoint.sh"]
