# 1. Base image 선택: Python 3.10을 사용
FROM python:3.10-slim

# 2. 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-distutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. 작업 디렉토리 설정: /app 폴더를 작업 디렉토리로 설정
WORKDIR /app

# 5. dependencies 설치: requirements.txt 파일을 복사하고 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-decouple

# 6. 소스 코드 복사: 현재 디렉토리의 모든 파일을 /app 디렉토리로 복사
COPY . /app/
COPY .env /app/.env

# 7. 포트 노출: Django 개발 서버가 사용하는 8000 포트를 노출
EXPOSE 8000

# 8. 서버 실행: Django 개발 서버를 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]