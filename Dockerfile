FROM python:3.11-slim-bullseye

WORKDIR /app

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN playwright install --with-deps chromium

COPY . .

RUN mkdir -p /app/data /app/downloads /app/logs

EXPOSE 5000

ENV FLASK_APP=web_app.py
ENV FLASK_ENV=production

CMD ["python", "web_app.py", "--host", "0.0.0.0", "--port", "5000"]
