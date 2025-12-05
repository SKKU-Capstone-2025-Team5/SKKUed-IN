FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    ca-certificates \
    curl \
    --no-install-recommends \
    && mkdir -p /usr/share/keyrings \
    # 1. 구글 서명 키를 다운로드해서 gpg 파일로 변환 저장
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg \
    # 2. 저장된 키를 참조하도록 레포지토리 추가 (signed-by 옵션 사용)
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    # 3. 설치 진행
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "contest_crawler.py"]