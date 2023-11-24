# Краткое описание
Сайт, который позволяет делиться своими рецептами с другими пользователями, просматривать чужие рецепты и составлять список необходимых продуктов для их приготовления. Регистрация и аутентификация реализованы через djoser. Приложение запускается в нескольких Docker-контейнерах: база данных (PostgreSQL), бэкенд (API на базе Django и REST Framework), фронтэнд (за который я не отвечал)  и сервер (nginx). Также с помощью GitHub Actions реализованы тестирование и деплой на удалённый сервер в Яндекс.Облаке.

# IP Сервера
Сервер доступен по адресу: http://51.250.89.99/ или по доменному имени http://andredog.ddns.net/, но так же его можно развернуть и на локальном компьюторе

# Пользователь для быстрого входа на удалённом сервере
Почта: user@mail.com </br>
Пароль: useruser

# Запуск на локальном компьюторе
Для запуска вам потребуется Docker, так что предварительно зарегистрируйтесь в нём, скачайте его и войдите в него и на локальном компьюторе с помощью команды:
```
docker login
```
Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Ander-dog/foodgram.git
```
```
cd foodgram
```

Перейти в папку `infra-local` и создайть в ней файл `.env`:
```
cd infra-local/
touch .env
```

Открыть файл и заполнить его по образцу:
```
nano .env
```
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

Запуск образа приложения:

```
sudo docker-compose up -d --build
```

Применить миграции:

```
sudo docker-compose exec backend python manage.py migrate
```

Создать суперюзера (нужно будет придумать логин, почту и пароль):

```
sudo docker-compose exec backend python manage.py createsuperuser
```

Заполнить базу данных:

```
sudo docker-compose exec backend python manage.py fill -a
```

По ключу `-a` можно загрузить в базу данных тэги, ингредиенты, пару пользователей и несколько рецептов, чтобы не заполнять сайт самостоятельно. Однако необходимы для работы приложения только тэги и ингредиенты.

Только их можно загрузить по ключу -it

```
sudo docker-compose exec backend python manage.py fill -it
```
### Документация к API доступна после запуска

```
http://localhost/api/docs/
```

# Стек технологий

- Python (язык разработки бэкенда)

- Django (фрэймворк приложения)
- Django ORM (для работы с базами данных)
- Django REST Framework (фреймворк API)
- Djoser (для аутентификации в API)
- PostgreSQL (База данных)
- Gunicorn (WSGI-сервер, соединяющий проект и HTTP-сервер)
- Nginx (HTTP-сервер)
- Docker (Контейнеризация приложения)
- Яндекс.Облако (Облачный сервер)
- GitHub Actions (CI и CD проекта)

# Автор

[Андрей А.](https://github.com/Ander-dog)

![workflow status](https://github.com/Ander-dog/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)