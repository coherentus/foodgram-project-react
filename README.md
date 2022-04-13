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
    * Перед запуском проекта на продакш-сервере соответствующие образы должны быть сформированы на DockerHub.


2. Последовательный план действий.
    * Создать на удалённом сервере папку для проекта, например "foodgramm-react".
    * Скопировать в эту папку содержимое папки "remote_srv".
    * В файле ".env.temlate" откорректировать необходимые настройки, переименовать его или скопировать под именем ".env".
    * В файле "docker-compose.yml" указать свои имена образов на DockerHub.
    * Скопировать папку "docs" из корня данного репозитория в папку проекта на удалённом сервере для доступа к документации API или исключить(закомментировать) настройки этой папки из "docker-compose.yml".
    * Скопировать папку "data" из корня данного репозитория в папку проекта на удалённом сервере для возможности подгрузки в БД сервера заготовок фикстур к моделям продуктов и тегов.
    * Находясь в папке проекта запустить первоначальную инициализацию:
        ```bash
        docker-compose up --build -d
        ```
    _Первоначальная сборка контейнеров из образов может занять заметное время._
    * После удачного запуска объединения из трёх контейнеров проекта
        * необходимо:
            * инициализировать БД. В терминах Django - применить миграции:
            ```bash
            sudo docker-compose exec backend python manage.py migrate
            ```
            * создать суперпользователя:

            ```bash
            sudo docker-compose exec backend python manage.py createsuperuser
            ```
        * необязательно, но полезно(отображение административных страниц в удобном формате значительно упрощает наглядность сопровождения проекта):
            * собрать статику:
            ```bash
            sudo docker-compose exec backend python manage.py collectstatic
            ```
        * необязательно, но возможно:
            * загрузить заготовку БД для таблиц теков и продуктов. Имена таблиц и файлов прописаны в коде management-команды.
            ```bash
            sudo docker-compose exec backend python manage.py load_data
            ```
    * Дальнейшая работа по развёртыванию доработок проекта автоматизирована механизмом GiHub-actions. На текущий момент workflow отлеживает событие "push" в ветку "master".
    
3. Необходимые для запуска проекта переменные для Gihub-actions:
    * относящиеся к Dockerhub:
        * DOCKER_USERNAME
        * DOCKER_PASSWORD
        
        
        _соответственно, логин и пароль на DockerHub. В workflow имена образов для Dockerhub прописаны в коде, можно также заменить на конфигурируемые через секреты._

    * относящиеся к удалённому серверу(production):
        * HOST
        * USER
        * SSH_KEY
        * PASSPHRASE
        * PROJECT_FOLDER


        _используются в workflow для логина на сервер и перехода в папку проекта_
    * относящиеся к настройкам кода backend-а и сценариев сборки образов Docker:
        * ALLOWED_HOSTS
        * SECRET_KEY
        * DEBUG
        * DB_ENGINE
        * DB_HOST
        * DB_NAME
        * DB_PORT        
        * POSTGRES_PASSWORD        
        * POSTGRES_USER


        _используются в workflow для генерации файла "**.env**" в папке проекта, а также значения используются в контейнере "**backend**" для инициализации и работы django-проекта через его "**settins.py**". Для ALLOWED_HOSTS несколько значений указываются через пробел. Значения DB_NAME, POSTGRES_USER и POSTGRES_PASSWORD также используются в контейнере "**db**" для инициализации БД PostgreSQL._
    * для отсылки сообщения в Телеграм на завершающем этапе workflow:
        * TELEGRAM_TO  - ID телеграм-аккаунта того, кому будет послано сообщение.
Узнать свой ID можно у бота @userinfobot.
        * TELEGRAM_TOKEN - токен бота, созданного тем, кому будет послано сообщение.
Получить этот токен можно у бота @BotFather.





