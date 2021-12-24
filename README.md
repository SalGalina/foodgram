# Дипломный проект foodgram
![FoodGram CI & CD](https://github.com/SalGalina/foodgram-project-react/workflows/foodgram-workflow.yml/badge.svg)

**FoodGram**: [API](http://www.gals.ml/api/v1/),
[Админка](http://www.gals.ml/admin/),
[Документация](http://www.gals.ml/redoc/).

## Продуктовый менеджер

### Проект позволит пользователям

- создать свой профиль,
- публиковать рецепты,
- добавлять понравившиеся рецепты в избранное,
- подписываться на любимых авторов,
- формировать список покупок для выбранных рецептов.

### Технологии

- Python 3.7-slim
- Django 2.2.6
- Django REST Framework 3.12.4
- Django REST Framework SimpleJWT 4.7.2 + Djoser==2.1.0
- Gunicorn 20.1.0
- Nginx 1.21.3-alpine
- PostgreSQL 13.0-alpine

### Шаблон заполнения .env-файла

- DB_ENGINE= <сервер базы данных>
- POSTGRES_DB= <имя базы данных>
- POSTGRES_USER=
- POSTGRES_PASSWORD=
- DB_HOST= <название сервиса (контейнера базы данных)>
- DB_PORT= <порт для подключения к БД>

- DEBUG=
- SECRET_KEY=
- ALLOWED_HOSTS= <IP-адрес и доменные адреса сайта через пробел>

### Развертывание и запуск проекта

- Установите Docker, Docker Compose

```bash
#!/bin/bash
sudo apt remove docker docker-engine docker.io containerd runc
sudo apt update
sudo apt install \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg-agent \
  software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install docker-ce docker-compose -y
```

- Скачайте репозиторий с проектом с GitHub

```bash
#!/bin/bash
git clone git@github.com:SalGalina/yamdb_final.git
```

- Скачайте образ проекта с DockerHub

```bash
#!/bin/bash
sudo docker pull salgalina/yamdb_final:latest
```

- Настройте переменные окружения в .env файле и на GitHub Actions

- измените IP-адрес и доменные имена в infra/nginx/default.conf

- Локальный запуск приложения:

```bash
#!/bin/bash
sudo docker-compose up -d --build
```

- Запустите миграции:

```bash
#!/bin/bash
sudo docker-compose exec web python manage.py migrate
```

- Создайте суперпользователя:

```bash
#!/bin/bash
sudo docker-compose exec web python manage.py createsuperuser
```

- Соберите статику:

```bash
#!/bin/bash
sudo docker-compose exec web python manage.py collectstatic --no-input
```

- Загрузите данные в базу при необходимости:

```bash
#!/bin/bash
scp fixtures.json <username>@<domain_name or IP>:<home_dir>
sudo docker cp fixtures.json <container_name or container_id>:<path_to_workdir>
sudo docker-compose exec web python manage.py shell
>>> from django.contrib.contenttypes.models import ContentType
>>> ContentType.objects.all().delete()
>>> quit()
sudo docker-compose exec web python manage.py loaddata fixtures.json
```

### Авторы

Салошина Галина
