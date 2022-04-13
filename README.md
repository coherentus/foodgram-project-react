# praktikum_new_diplom
[![Django-app workflow](https://github.com/coherentus/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/coherentus/foodgram-project-react/actions/workflows/main.yml)

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


*** Разворачивание проекта на сервере:

1. Необходимые условия и замечания:
    * Проект работает в связке контейнеров Docker. Минимальная версия Docker-compose - 3.3
    * Перед этапом эксплуатации необходим подготовительный этап.
    * Схема модернизации и сопровождения проекта включает в себя репозиторий на GitHub, создание и хранение образов частей проекта на DockerHub посредством подсистемы workflow GitHub-actions.


2. Последовательный план действий.
    * Создать на удалённом сервере папку для проекта, например "foodgramm-react".
    * Скопировать в эту папку содержимое папки "remote_srv".
    * В файле ".env.temlate" откорректировать необходимые настройки, переименовать его или скопировать под именем ".env".
    * В файле "docker-compose.yml" указать свои имена образов на DockerHub.
    * Скопировать папку "docs" из корня данного репозитория в папку проекта на удалённом сервере для доступа к документации API или исключить(закомментировать) настройки этой папки из "docker-compose.yml".
    * Скопировать папку "data" из корня данного репозитория в папку проекта на удалённом сервере для возможности подгрузки в БД сервера заготовок фикстур к моделям продуктов и тегов.
    
