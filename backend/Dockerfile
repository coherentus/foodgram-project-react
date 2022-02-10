FROM python:3.8.5

WORKDIR /code

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r ./requirements.txt

RUN pip install gunicorn==20.1.0

COPY . .

CMD gunicorn foodgram_backend.wsgi:application --bind 0.0.0.0:8000
