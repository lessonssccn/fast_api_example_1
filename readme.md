# Порсотое fastapi приложение
### Что показно
* Простой CRUD
* Разбиение на пакеты и модули
* json response 
* request body json
* Параметрами запроса
* Запросы с изменяемой частью пути
* Взаимодейсвтие с БД sqlite
* Простой набор тестов
* Использовния разных бд для запуска и тестирования

### Подготовка окружения
```
git clone https://github.com/lessonssccn/fast_api_example_1.git
```
```
cd fast_api_example_1
```
```
python3 -m venv env
```
```
source env/bin/activete
```
```
pip install -r requirements.txt
```

### Запуск
отсаваясь в папке fast_api_example_1
```
uvicorn app.main:app --reload
```
Запускаестся по умолчанию на адрессе 127.0.0.1 на порту 8000
```
http://127.0.0.1:8000
```
### Запуск тестов
отсаваясь в папке fast_api_example_1
```
pytest
```
### Документайия после запуска
```
http://127.0.0.1:8000/docs
```
