# praktikum_new_diplom

Для запуска проекта локально неоходимы:

* система с установленым и работоспособным docker в сочетании с его расширением docker-compose.
* файл ```.env``` в папке ```backend``` следующего содержания:

    ```
    SECRET_KEY='секретный ключ Django'
    POSTGRES_DB=имя_базы_данных
    POSTGRES_USER=логин_в_бд
    POSTGRES_PASSWORD=пароль_в_бд
    DB_HOST=db  # имя контейнера БД, должно совпадать с тем, что прописано в сценариях Docker-а
    DB_PORT=5432
    DEBUG=TRUE
    ALLOWED_HOSTS=* backend localhost 127.0.0.1  # имена/IP хостов через пробел
    ```

    В папке ```backend``` есть для этого заготовка ```.env.txt```

Запуск всей совокупности контейнеров проекта осуществляется из папки **infra** командой ```sudo docker-compose up -d```

Для свежесозданного репозитория после первого запуска следующие действия

* **Необходимы**

    Инициализация БД. В терминах Django - применить миграции:

    ```bash
    sudo docker-compose exec backend python manage.py migrate
    ```

    Ссоздание суперпользователя:

    ```bash
    sudo docker-compose exec backend python manage.py createsuperuser
    ```

* **Необязательны, но полезны**


    Загрузка ингредиентов:

    ```bash
    sudo docker-compose exec backend python manage.py load_data
    ```

    Сборка статики:

    ```bash
    sudo docker-compose exec backend python manage.py collectstatic
    ```

