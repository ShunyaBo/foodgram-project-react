# Проект Foodgram
___
[![Python 3](https://img.shields.io/badge/-Python-3670A0?style=for-the-badge&logo=Python&logoColor=ffdd54)](https://www.python.org/) [![Django](https://img.shields.io/badge/-Django-23092E20?style=for-the-badge&logo=Django&logoColor=white)](https://www.djangoproject.com/) [![Django REST framework](https://img.shields.io/badge/Django%20REST%20framework-ff1709?style=for-the-badge&logo=django&logoColor=white&color=00e5cc&labelColor=00e5cc)](https://www.django-rest-framework.org/) [![Pytest](https://img.shields.io/badge/-Pytest-grey?style=for-the-badge&logo=Pytest)](https://docs.pytest.org/en/6.2.x/) [![Postman](https://img.shields.io/badge/-Postman-00BFFF?style=for-the-badge&logo=Postman)](https://www.postman.com/) [![JWT + Djoser](https://img.shields.io/badge/-JWT%20%2B%20Djoser-black?style=for-the-badge&logo=JSON%20web%20tokens)](https://djoser.readthedocs.io/en/latest/introduction.html) [![Docker](https://img.shields.io/badge/-Docker-2496ed?style=for-the-badge&logo=Docker&logoColor=white)](https://www.docker.com/) [![React](https://img.shields.io/badge/-React-grey?style=for-the-badge&logo=React)](https://react.dev/) [![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-lightgrey?style=for-the-badge&logo=PostgreSQL)](https://www.postgresql.org/) [![Nginx](https://img.shields.io/badge/-Nginx-CD853F?style=for-the-badge&logo=Nginx&logoColor=white)](https://nginx.org/ru/) [![Gunicorn](https://img.shields.io/badge/-Gunicorn-298729?style=for-the-badge&logo=Gunicorn&logoColor=white)](https://gunicorn.org/#docs)
___

### Описание проекта

Проект "Foodgram" – это "продуктовый помощник". На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект доступен по [адресу](https://kodzha.ddns.net).

Для неавторизированных пользователей доступно:
- Зарегистрироваться / создать аккаунт.
- Просматривать рецепты на главной странице.
- Просматривать отдельные страницы рецептов.
- Просматривать страницы пользователей.
- Фильтровать рецепты по тегам.


Для авторизованных пользователей доступно:
- Авторизация в системе под своим логином и паролем.
- Выходить из системы (разлогиниваться).
- Менять свой пароль.
- Создавать/редактировать/удалять собственные рецепты.
- Просматривать рецепты на главной странице.
- Просматривать страницы пользователей.
- Просматривать отдельные страницы рецептов.
- Фильтровать рецепты по тегам.
- Работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов.
- Работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл с количеством необходимых ингредиентов для рецептов из списка покупок.
- Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.


Администратор обладает всеми правами авторизованного пользователя. Плюсом он может:
- Изменять пароль любого пользователя.
- Создавать/блокировать/удалять аккаунты пользователей.
- Редактировать/удалять любые рецепты.
- Добавлять/удалять/редактировать ингредиенты.
- Добавлять/удалять/редактировать теги.

___

## Установка и запуск проекта локально

1. Клонируйте репозиторий на свой компьютер:

    ```bash
    git clone git@github.com:ShunyaBo/foodgram-project-react.git

    cd foodgram-project-react
    ```
2. Создайте файл .env и заполните его своими данными. Перечень данных указан в файле .env.example.
3. Cоздайте и активируйте виртуальное окружение:

    ```bash
    python3 -m venv venv
    
    Linux: source venv/bin/activate
    Windows: source venv/Scripts/activate
    ```

4. Установить зависимости из файла requirements.txt:

    ```bash
    python3 -m pip install --upgrade pip

    pip install -r requirements.txt
    ```

5. В директории foodgram-project-react/infra/ запустите docker-compose:

    ```bash
    cd infra

    docker-compose up
    ```

6. Когда контейнеры собраны в новом окне терминала выполните миграции:

    ```bash
    docker-compose exec backend python manage.py migrate
    ```

7. Создайте суперпользователя:

    ```bash
    docker-compose exec backend python manage.py createsuperuser
    ```

8. Загрузите статику:

    ```bash
    docker-compose exec backend python manage.py collectstatic --no-input 
    ```

9. Проверьте работу проекта по ссылке:

    ```bash
    http://localhost/
    ```

10. Все доступные ендпоинты можно посмотреть в документации по ссылке:
    ```bash
    http://localhost/api/docs/
    ```

11. Зайдите в админ-панель по ссылке:

    ```bash
    http://localhost/admin
    ```

12. Загрузите в БД информацию об ингредиентах через админ-панель:

    - в админ-панеле зайдите в раздел ингредиенты
    - нажмите кнопку - импорт
    - выберете файл с разрешением json из папки data
    - выберете формат - json и импортируйте.

___

### Настройка CI/CD

1. Файл workflow уже написан. Он находится в директории

    ```bash
    foodgram-project-react/.github/workflows/main.yml
    ```

2. Для адаптации его на своем сервере добавьте Secrets в GitHub Actions:

    ```bash
    DOCKER_USERNAME                # имя пользователя в DockerHub
    DOCKER_PASSWORD                # пароль пользователя в DockerHub
    HOST                           # ip_address удалённого сервера
    USER                           # логин на удалённом сервере
    SSH_KEY                        # приватный ssh-ключ компьютера, с которого будет происходить
                                   # подключение к удалённому серверу (cat ~/.ssh/id_rsa)
    SSH_PASSPHRASE                 # кодовая фраза (пароль) для ssh-ключа

    ```
___

### Запустить проект на боевом сервере:

1. Установите на боевом сервере Docker и Docker Compose. Для запуска необходимо установить Docker и Docker Compose. Подробнее об установке на других платформах можно узнать на [официальном сайте](https://docs.docker.com/engine/install/).
    ```bash
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt-get install docker-compose-plugin 
    ```

2. Проверьте, что Docker работает:
    ```bash
    sudo systemctl status docker
    ```
Подробнее про установку можно прочитать [здесь](https://docs.docker.com/engine/install/ubuntu/)

3. Скопируйте на сервер файлы docker-compose.production и default.conf и .env:

    ```bash
    scp docker-compose.yml <логин_на_сервере>@<IP_сервера>:/home/<логин_на_сервере>/docker-compose.yml
    scp nginx.conf <логин_на_сервере>@<IP_сервера>:/home/<логин_на_сервере>/nginx.conf
    ```

4. Выполните команды:

    ```bash
    git add .
    git commit -m "Коммит"
    git push
    ```

После этого будут запущены процессы workflow:

- проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8) и запуск pytest
- сборка и доставка докер-образа для контейнера backend на Docker Hub
- автоматический деплой проекта на боевой сервер


5. После успешного завершения процессов workflow на сервере выполним следующие команды:

- Сделать миграции: 

    ```bash
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
    ```

- Собрать статические файлы для корректного отображения страниц и скопируйте ее в др директорию: 

    ```bash
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
    sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /app/static/static/
    ```

- Создать суперюзера:

    ```bash
    sudo docker compose -f docker-compose.production.yml exec -it backend python manage.py createsuperuser 
    ```

- Загрузить в БД информацию об ингредиентах через админ-панель:

    - в админ-панеле зайдите в раздел ингредиенты;
    - нажмите кнопку - импорт;
    - выберете файл с разрешением json из папки data;
    - выберете формат - json и импортируйте.

___
### Автор
[Mariya - ShunyaBo](https://github.com/ShunyaBo)