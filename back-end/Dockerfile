# Dockerfile.backend

# 기본 이미지 설정 (Python 3.11)
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# 애플리케이션 소스 코드 복사
COPY . /app

# 서버 실행 포트 개방
EXPOSE 8000

# Uvicorn을 사용해 FastAPI 앱 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]