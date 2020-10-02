Разработать REST-API для управления списком регионов и городов, которые в них входят
Необходимо реализовать выборку регионов, выборку городов по региону, CRUD для городов и регионов.
Для неавторизованного пользователя должны быть доступны только выборки данных.
Для проверки нужно создать в базе 1-2 пользователей, управление их записями через API не предполагается.

В качестве БД рекомендуется использовать postgresql, Flask - как фреймворк для создания веб-сервера.


# Run app

```bash 
docker run --name postgres_5302 \
    -e POSTGRES_PASSWORD=mysecretpassword \
    -e POSTGRES_DB=postgres_5302 \
    -p 5432:5432 -d postgres

python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
python3 app.py

```

# Tests
```bash
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
pytest
```


# Run with Docker
```bash

docker run --name postgres_5302 \
    -e POSTGRES_PASSWORD=mysecretpassword \
    -e POSTGRES_DB=postgres_5302 \
    -p 5432:5432 -d postgres

docker run --name university -d -p 5000:5000 --link postgres_5302:db  serkin/university

curl 'http://127.0.0.1:5000/countries'
# or
pytest _test_api_independent.py
```

Решения и обоснования:
- Попытался все укутать в одном файле чтобы легче проверить работу. Конечно для прод системы структуру бы улучшил.
- Тесты написал двух типов
    - test_api.py - Для тестирования в разработке
    - _test_api_independent.py - Для тестирования независимо от приложения(немного тестов) ```python2 _test_api_independent.py```

Чтобы бы я сделал для улучшения при неограниченном времени)
- Добавил бы setup.py для удобного разворачивания локально
- sdn к базе вынес или в конфиг или в .env
- Пагинацию к спискам
- Настроил бы исключения чтобы больше полезной информации отдавали
- Не удалял бы записи, а помечал как удаленные
- docker-compose - Так как по умолчанию не у всех стоит не стал добавлять
- Документация
- Tесты через pytest _params