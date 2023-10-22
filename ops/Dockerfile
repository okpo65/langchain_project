# 베이스 이미지 설정
FROM python:3.9


ENV DJANGO_SETTINGS_MODULE config.settings

# 작업 디렉터리 설정
WORKDIR /langchain

COPY ../requirements.txt /langchain/

# 의존성 설치
RUN pip install -r requirements.txt

COPY . /langchain/
COPY .env .env
EXPOSE 80

# Django 애플리케이션 실행 명령
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]