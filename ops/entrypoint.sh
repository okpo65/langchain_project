#!/bin/sh

# 마이그레이션 실행
python manage.py migrate

python manage.py runserver 0.0.0.0:80