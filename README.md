# Pract 3
## Ex 1
```Python
import re

data = '''dakak30@yahoo.com|false +77995231033
calan62@yandex.ru|false +77610387005
zanubij49@gmail.com|false +73308657933
N +7(916)9985670 Лев З. Зибефий
N 8-912-268-5440 Ян Ф. Балигук
N 8905148-3339 Лев У. Сонорин
8(913)448-51-90 Да Табушберг, А.К. 0.05
903-345-34-34 Да Нушешянц, Г.И. 0.24
903-34-334-34 Да Вефук, А.Г. 0.71
903-34-33434 Нет Мулигин, Ф.М. 0.08
Мефский, К.Д. 04/04/22 0.2
Мафусяк, Д.Р. 04/12/23 0.5
Вумук, С.С. 99/10/08 0.1
Вокезман, А.Е. 04/12/10 0.9
Не выполнено 1999-12-01 ramil_30@rambler.ru
Не выполнено 1999-12-01 ramil_30@rambler.ru
Не выполнено 1999-12-01 ramil_30@rambler.ru
Не выполнено 2001-09-12 busman96@yandex.ru
Не выполнено 2000-06-22 dmitrij47@yahoo.com
Выполнено 2002-05-17 vaceslav86@yandex.ru'''

emails = re.findall(r'\w+(?:[.-]?\w+)*@\w+(?:[.-]?\w+)*\.\w{2,3}', data)

for email in emails:
    print(email)

```

```Shell
dakak30@yahoo.com
calan62@yandex.ru
zanubij49@gmail.com
ramil_30@rambler.ru
ramil_30@rambler.ru
ramil_30@rambler.ru
busman96@yandex.ru
dmitrij47@yahoo.com
vaceslav86@yandex.ru

```
## Ex2
```Python
import re

data = '''dakak30@yahoo.com|false +77995231033
calan62@yandex.ru|false +77610387005
zanubij49@gmail.com|false +73308657933
N +7(916)9985670 Лев З. Зибефий
N 8-912-268-5440 Ян Ф. Балигук
N 8905148-3339 Лев У. Сонорин
8(913)448-51-90 Да Табушберг, А.К. 0.05
903-345-34-34 Да Нушешянц, Г.И. 0.24
903-34-334-34 Да Вефук, А.Г. 0.71
903-34-33434 Нет Мулигин, Ф.М. 0.08'''

phones = re.findall(r'(?:\+7|8|\d{3})[-\s]?\(?\d{2,3}\)?[-\s]?\d{2,3}[-\s]?\d{2}[-\s]?\d{2,3}', data)

for phone in phones:
    print(phone)

```

```Shell
+77995231033
+77610387005
+73308657933
+7(916)9985670
8-912-268-5440
8905148-3339
8(913)448-51-90
903-345-34-34
903-34-334-34
903-34-33434
```

# Pract 4

#### Установка виртуального окружения (venv) на Ubuntu:

1. Установить модуль `venv`:
   ```sh
   sudo apt install python3-venv
   ```

2. Создать виртуальное окружение:
   ```sh
   python3 -m venv venv
   ```
   
3. Активировать виртуальное окружение:
   ```sh
   source venv/bin/activate
   ```

#### Управление зависимостями

Чтобы зафиксировать текущие версии в файл `requirements.txt`:

```sh
pip freeze > requirements.txt
```

Установка всех зависимостей проекта:

```sh
pip install -r requirements.txt
```

# Pract5-6
```Python
import requests

url = "http://api.openweathermap.org/data/2.5/weather"
params = {
    "q": "London",
    "appid": "my_api_key",  
    "units": "metric",
    "lang": "ru"
}

headers = {
    "Content-Type": "application/json",
    "User-Agent": "my-weather-app"
}

response = requests.get(url, params=params, headers=headers)

print("Заголовки ответа от сервера:")
print(response.headers)

print("\nТело ответа от сервера:")
print(response.json())
```

```Shell
Заголовки ответа от сервера:
{
    'Server': 'openresty',
    'Date': 'Tue, 10 Oct 2023 19:30:53 GMT',
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': '524',
    'Connection': 'keep-alive',
    'X-Cache-Key': '/data/2.5/weather?APPID=your_api_key&lang=ru&q=London&units=metric',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Allow-Methods': 'GET, POST',
}

Тело ответа от сервера:
{
    'coord': {'lon': -0.13, 'lat': 51.51},
    'weather': [{'id': 300, 'main': 'Drizzle', 'description': 'легкая морось', 'icon': '09d'}],
    'base': 'stations',
    'main': {
        'temp': 12.34,
        'feels_like': 10.95,
        'temp_min': 11.0,
        'temp_max': 13.89,
        'pressure': 1012,
        'humidity': 87
    },
    'visibility': 10000,
    'wind': {'speed': 4.12, 'deg': 80},
    'clouds': {'all': 90},
    'dt': 1633892400,
    'sys': {
        'type': 1,
        'id': 1414,
        'country': 'GB',
        'sunrise': 1633853845,
        'sunset': 1633892782
    },
    'timezone': 3600,
    'id': 2643743,
    'name': 'London',
    'cod': 200
}

```