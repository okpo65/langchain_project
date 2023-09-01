# 베이스 이미지 설정
FROM python:3.9

# 작업 디렉터리 설정
WORKDIR /llm

COPY ../requirements.txt /llm/

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

COPY . /llm/

EXPOSE 80

# Django 애플리케이션 실행 명령
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]