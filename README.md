### Hexlet tests and linter status:
[![Actions Status](https://github.com/PrefAir0/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/PrefAir0/python-project-83/actions)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=PrefAir0_python-project-83&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=PrefAir0_python-project-83)

**Page Analyzer** — Приложение на базе Flask. Оно позволяет анализировать сайты на доступность и извлекать данные.

## Особенности проекта
* Построен на веб-фреймворке **Flask**
* Данные хранятся в реляционной базе данных **PostgreSQL**
* Валидация и нормализация URL
* Стили написаны при помощи **Bootstrap 5**

## Требования
* PostgreSQL 15+
* Пакетный менеджер [uv]

## Установка и запуск локально

* Установи зависимости с помощью uv
* Создайте .env и укажите в нем [DATABASE_URL=postgresql://user:password@localhost:5432/page_analyzer] и ваш [SECRET_KEY]
* Запустите проект локально uv run flask --debug --app page_analyzer:app run
