# Проект Foodgram
___
[![Python 3](https://img.shields.io/badge/-Python%203-lightgrey)](https://www.python.org/) [![Django](https://img.shields.io/badge/-Django-lightgrey)](https://www.djangoproject.com/) [![Django REST framework](https://img.shields.io/badge/-Django%20REST%20framework-lightgrey)](https://www.django-rest-framework.org/) [![Pytest](https://img.shields.io/badge/-Pytest-lightgrey)](https://docs.pytest.org/en/6.2.x/) [![Postman](https://img.shields.io/badge/-Postman-lightgrey)](https://www.postman.com/) [![JWT + Djoser](https://img.shields.io/badge/-JWT%20%2B%20Djoser-lightgrey)](https://djoser.readthedocs.io/en/latest/introduction.html) [![Docker](https://img.shields.io/badge/-Docker-lightgrey)](https://www.docker.com/) [![React](https://img.shields.io/badge/-React-lightgrey)](https://react.dev/) [![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-lightgrey)](https://www.postgresql.org/) [![Nginx](https://img.shields.io/badge/-Nginx-lightgrey)](https://nginx.org/ru/) [![Gunicorn](https://img.shields.io/badge/-Gunicorn-lightgrey)](https://gunicorn.org/#docs)
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

## Установка

1. Клонируйте репозиторий на свой компьютер:

    ```bash
    git clone git@github.com:ShunyaBo/foodgram-project-react.git
    ```
    ```bash
    cd foodgram-project-react
    ```
2. Создайте файл .env и заполните его своими данными. Перечень данных указан в файле .env.example.
3. Cоздайте и активировать виртуальное окружение:

    ```bash
    python -m venv venv
    
    Linux: source venv/bin/activate
    Windows: source venv/Scripts/activate
    ```

4. Установить зависимости из файла requirements.txt:

    ```bash
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

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

    TELEGRAM_TO                    # id телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
    TELEGRAM_TOKEN                 # токен бота (получить токен можно у @BotFather, /token, имя бота)
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

Скопировать на сервер файлы docker-compose.yaml и default.conf:

```
scp docker-compose.yml <логин_на_сервере>@<IP_сервера>:/home/<логин_на_сервере>/docker-compose.yml
scp nginx.conf <логин_на_сервере>@<IP_сервера>:/home/<логин_на_сервере>/nginx.conf

```



Выполнить команды:

*   git add .
*   git commit -m "Коммит"
*   git push

После этого будут запущены процессы workflow:

*   проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8) и запуск pytest
*   сборка и доставка докер-образа для контейнера web на Docker Hub
*   автоматический деплой проекта на боевой сервер
*   отправка уведомления в Telegram о том, что процесс деплоя успешно завершился

После успешного завершения процессов workflow на боевом сервере должны будут выполнены следующие команды:

```
sudo docker-compose exec web python manage.py migrate

sudo docker-compose exec web python manage.py collectstatic --no-input 
```

Затем необходимо будет создать суперюзера и загрузить в базу данных информацию об ингредиентах:

```
sudo docker-compose exec web python manage.py createsuperuser

```

```
sudo docker-compose exec web python manage.py load_data_csv --path <путь_к_файлу> --model_name <имя_модели> --app_name <название_приложения>

```

### Как запустить проект локально в контейнерах:

Клонировать репозиторий и перейти в него в командной строке:

``` git@github.com:mariyabykova/foodgram-project-react.git ``` 
``` cd foodgram-project-react ``` 

Запустить docker-compose:

```
docker compose up

```

После окончания сборки контейнеров выполнить миграции:

```
docker-compose exec web python manage.py migrate

```

Создать суперпользователя:

```
docker-compose exec web python manage.py createsuperuser

```

Загрузить статику:

```
docker-compose exec web python manage.py collectstatic --no-input 

```

Проверить работу проекта по ссылке:

```
http://localhost/
```
___
### Как запустить проект локально:

Клонировать репозиторий и перейти в него в командной строке:

``` git clone <ссылка с github> ``` 
``` cd foodgram-project-react ``` 

Создать и активировать виртуальное окружение:

``` python3 -m venv venv ``` 

* Если у вас Linux/macOS:
    ``` source venv/bin/activate ``` 

* Если у вас Windows:
    ``` source venv/Scripts/activate ```
    
``` python3 -m pip install --upgrade pip ``` 

Установить зависимости из файла requirements:

``` pip install -r requirements.txt ``` 

Выполнить миграции:

``` python3 manage.py migrate ``` 

Запустить проект:

``` python3 manage.py runserver ``` 
___
### В API доступны следующие эндпоинты:

* ```/api/users/```  Get-запрос – получение списка пользователей. POST-запрос – регистрация нового пользователя. Доступно без токена.

* ```/api/users/{id}``` GET-запрос – персональная страница пользователя с указанным id (доступно без токена).

* ```/api/users/me/``` GET-запрос – страница текущего пользователя. PATCH-запрос – редактирование собственной страницы. Доступно авторизированным пользователям. 

* ```/api/users/set_password``` POST-запрос – изменение собственного пароля. Доступно авторизированным пользователям. 

* ```/api/auth/token/login/``` POST-запрос – получение токена. Используется для авторизации по емейлу и паролю, чтобы далее использовать токен при запросах.

* ```/api/auth/token/logout/``` POST-запрос – удаление токена. 

* ```/api/tags/``` GET-запрос — получение списка всех тегов. Доступно без токена.

* ```/api/tags/{id}``` GET-запрос — получение информации о теге о его id. Доступно без токена. 

* ```/api/ingredients/``` GET-запрос – получение списка всех ингредиентов. Подключён поиск по частичному вхождению в начале названия ингредиента. Доступно без токена. 

* ```/api/ingredients/{id}/``` GET-запрос — получение информации об ингредиенте по его id. Доступно без токена. 

* ```/api/recipes/``` GET-запрос – получение списка всех рецептов. Возможен поиск рецептов по тегам и по id автора (доступно без токена). POST-запрос – добавление нового рецепта (доступно для авторизированных пользователей).

* ```/api/recipes/?is_favorited=1``` GET-запрос – получение списка всех рецептов, добавленных в избранное. Доступно для авторизированных пользователей. 

* ```/api/recipes/is_in_shopping_cart=1``` GET-запрос – получение списка всех рецептов, добавленных в список покупок. Доступно для авторизированных пользователей. 

* ```/api/recipes/{id}/``` GET-запрос – получение информации о рецепте по его id (доступно без токена). PATCH-запрос – изменение собственного рецепта (доступно для автора рецепта). DELETE-запрос – удаление собственного рецепта (доступно для автора рецепта).

* ```/api/recipes/{id}/favorite/``` POST-запрос – добавление нового рецепта в избранное. DELETE-запрос – удаление рецепта из избранного. Доступно для авторизированных пользователей. 

* ```/api/recipes/{id}/shopping_cart/``` POST-запрос – добавление нового рецепта в список покупок. DELETE-запрос – удаление рецепта из списка покупок. Доступно для авторизированных пользователей. 

* ```/api/recipes/download_shopping_cart/``` GET-запрос – получение текстового файла со списком покупок. Доступно для авторизированных пользователей. 

* ```/api/users/{id}/subscribe/``` GET-запрос – подписка на пользователя с указанным id. POST-запрос – отписка от пользователя с указанным id. Доступно для авторизированных пользователей

* ```/api/users/subscriptions/``` GET-запрос – получение списка всех пользователей, на которых подписан текущий пользователь Доступно для авторизированных пользователей. 
___
### Автор
[Mariya - ShunyaBo](https://github.com/ShunyaBo)