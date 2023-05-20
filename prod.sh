#!/bin/bash

if [ -f .env ]; then
  if grep -q "PROD=true" .env; then
    echo "PROD flag is set to true in the .env file"
  else
    echo "PROD flag is not set to true in the .env file, exiting..."
    exit 1
  fi
else
  echo ".env file is not present, exiting..."
  exit 1
fi

if [ -d ~/appdata ]; then
  echo "appdata folder exists, proceeding..."
else
  echo "appdata folder does not exist, creating..."
  mkdir ~/appdata
  mkdir ~/appdata/new_forecast
  touch ~/appdata/new_forecast/db.sqlite3
fi

git pull origin main  
docker stop new_forecast
docker rm new_forecast
docker rmi new_forecast

docker buildx build . -t new_forecast
docker run \
	-d \
	--name new_forecast \
	--restart always \
	-v ~/appdata/new_forecast/db.sqlite3:/app/db.sqlite3 \
	-p 8000:8000 \
	new_forecast

docker exec new_forecast python manage.py makemigrations
docker exec new_forecast python manage.py migrate
