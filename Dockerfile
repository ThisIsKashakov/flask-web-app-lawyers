FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential nginx git certbot python3-certbot-nginx && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /app/uploads && \
    chown -R root:root /app/uploads

EXPOSE 80 443

CMD bash -c "\
  gunicorn --workers 3 --bind 127.0.0.1:8000 main:app & \
  nginx -g 'daemon off;'"
