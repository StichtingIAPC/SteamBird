#!/bin/sh
# Author: Rolf van Kleef
# Licensed under LGPL v2

python manage.py migrate

uwsgi \
    --chdir "/project/"\
    --static-map "/static=static" \
    --http=0.0.0.0:8000 \
    --processes=4 \
    --harakiri=20 \
    --vacuum \
    -b 32768 \
    --module=steambird.wsgi:application
