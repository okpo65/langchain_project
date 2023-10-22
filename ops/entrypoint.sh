#!/bin/sh

# 마이그레이션 실행
python manage.py migrate

# 원래의 명령어 실행 (예: Gunicorn, UWSGI, 기타 등등)
exec "$@"