# praktikum_new_diplom
foodgram-project-react

# Начало работы с проектом:

# Перейти в папку с бэкендом

cd backend/

# Cоздать и активировать виртуальное окружение:

python -m venv env

source env/bin/activate

# Установить зависимости из файла requirements.txt:

python -m pip install --upgrade pip

pip install -r requirements.txt

# Выполнить миграции:

cd  foodgram/

python manage.py migrate

# Заполнить БД тестовыми данными:

python manage.py fill


# Запустить проект:

python manage.py runserver