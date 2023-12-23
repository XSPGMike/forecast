# Forecast Legends

## Local development environment

In order to setup this project for local development make sure to have a python interpreter ( 3.10 or higher ) and the pip package manager.

1. The project uses pipenv as a python virtualenv, you can install it with the following command:
```
$ python3 -m pip install pipenv
```

2. Setup the virtual environment and install the necessary dependencies
```
$ python3 -m pipenv install
```

3. Copy the .env.example file and edit it according to your setup

4. Migrate the database and create the superuser
```
$ python3 -m pipenv shell
$ python manage.py migrate
$ python manage.py createsuperuser
```

5. Start the uvicorn server
```
$ ./dev.sh
```

The web app should be available on port 8000
