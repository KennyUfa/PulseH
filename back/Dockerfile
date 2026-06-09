FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY back/ .

RUN mkdir -p /app/data && chmod 777 /app/data

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn back.wsgi:application --bind 0.0.0.0:8000 --workers 1 --timeout 120"]
