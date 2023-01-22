# Продуктовый помощник Foodgram 
Проект доступен по адресу http://51.250.30.50/signin

## Описание проекта Foodgram
«Продуктовый помощник»: приложение, на котором пользователи публикуют рецепты, подписываться на публикации других авторов и добавлять рецепты в избранное. Сервис «Список покупок» позволит пользователю создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Запуск с использованием CI/CD
Установить docker, docker-compose на сервере ВМ Yandex.Cloud:


### Создайте папку infra:

mkdir infra
Перенести файлы docker-compose.yml и nginx.conf на сервер.
scp docker-compose.yml username@server_ip:/home/<username>/
scp nginx.conf <username>@<server_ip>:/home/<username>/
Создайте файл .env в дериктории infra:
touch .env
Заполнить в настройках репозитория секреты .env
DB_ENGINE='django.db.backends.postgresql'
DB_NAME=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=db
DB_PORT='5432'
SECRET_KEY=
ALLOWED_HOSTS=
Скопировать на сервер настройки docker-compose.yml, nginx.conf из папки infra.

Запуск проекта через Docker
В папке infra выполнить команду, что бы собрать контейнер:
sudo docker compose up -d
Для доступа к контейнеру выполните следующие команды:

sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate --noinput
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
Дополнительно можно наполнить DB ингредиентами и тэгами:

sudo docker-compose exec backend python manage.py load_tags
sudo docker-compose exec backend python manage.py load_ingrs
### Запуск проекта в dev-режиме
Установить и активировать виртуальное окружение:
cd foodgram-project-react
python3 -m venv env
source /venv/bin/activated
### Установить зависимости из файла requirements.txt
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
Создайте базу и пользователя в Postgresql:
sudo -u postgres psql
CREATE DATABASE basename;
CREATE USER username WITH ENCRYPTED PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE basename TO username;
В папке с проектом создаем файл .env:
touch backend/foodgram/.env
С следующим содержанием db_name и db_user указываем свои:

DB_ENGINE='django.db.backends.postgresql'
DB_NAME='db_name'
POSTGRES_USER='db_user'
POSTGRES_PASSWORD='password'
DB_HOST='localhost'
DB_PORT='5432'
SECRET_KEY='put_your_code'
ALLOWED_HOSTS='127.0.0.1, localhost, backend, ip_server'
DEBUG=False
### Выполняем и применяем миграции, создаем суперпользователя и собираем статику:
python backend/manage.py makemigrations
python backend/manage.py migrate
python backend/manage.py createsuperuser
python backend/manage.py collectstatic --no-input


### Запускаем сервер командой:
python backend/manage.py runserver
Документация к API доступна после запуска
http://127.0.0.1/api/docs/
