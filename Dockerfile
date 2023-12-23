FROM python:3.10.13-bullseye
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system
COPY . .
COPY gunicorn.conf.py .
EXPOSE 8000
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "config.asgi:application", "-c", "gunicorn.conf.py", "-k", "uvicorn.workers.UvicornWorker"]
