#в пакте test написанны тесты для приложения
#в данном файле представленны тесты для тестирования эндпоинов 
#тесты не полные просто несколько примеров
import os#для работы с переменными окрыжения

#не самый лучший но рабочий способ смены бд для теста и обычного запуска
TEST_DB_FILE = "test.db" #имя файла для тестовой бд
SQLITE_DATABASE_URL_TEST = f"sqlite:///{TEST_DB_FILE}" #строка подключения для тестовой бд
os.environ['TESTING'] = 'True' #устанавливаем занчени переменной окружения TESTING
os.environ['SQLITE_TEST'] = SQLITE_DATABASE_URL_TEST #тоже самое для SQLITE_TEST в нее передаем строку подключения к тестовой бд
# делатли в файле app.main и app.db.database

from fastapi.testclient import TestClient #класс для клиена
from app.db.database import engine, Base #переменные и классы для инициализации и очистки дб
from app.main import app # импорт осоновного объекта приложения для тестирования
import pytest #импорт pytest для насктройки fixture - функйи которые надо запустить перед выполеннием теста
#дефолтные значения для нового пользователя и обновления для удобсвта 
new_user = {"name":"user_1", "password":"psw_1"}
update_user = {"name":"new_name", "password":"new_psw"}

#функция для обнуления бд чтобы для каждого теста бд была пустой 
@pytest.fixture()
def temp_db():
    Base.metadata.drop_all(bind=engine) #удаляем все таблицы из бд
    Base.metadata.create_all(bind=engine) #создаем таблицы поновой

#функция для добавления нового пользовтаеля нужна для тестирования поиска, удаления, обновления
@pytest.fixture()
def add_user():
    with TestClient(app) as client:
        response = client.post("/api/users/", json=new_user)

#все функции должны начинаться с test_
#просто как пример
def test_root():
    with TestClient(app) as client: #создаем обект класса для формирования запроса
        response = client.get("/")  #отпраялвем запрос на корень
    assert response.status_code == 200 # провека на статус 200 если двести то тест пройдет иначе генерируем ошибку прохождения теста

#тест добавления юзера
#как параметр передаем fixture temp_db чтобы очистить бд
def test_add_user(temp_db):
    with TestClient(app) as client:
        response = client.post("/api/users/", json=new_user)
    assert response.status_code == 201
    data = response.json() #получем тело ответа 
    assert data["success"] == True # success == True
    assert data["data"]["id"] == 1#  id в data при пустой таблицу будет всегда еденице 
    assert data["data"]["name"] == new_user["name"] #имя пользовтаеля в ответе должно соподать с именем пользоватея в запросе

#тест на получени юзера
#2 fixture очистить бд и доьавить тада пользователя
def test_get_user(temp_db, add_user):
    with TestClient(app) as client:
        response = client.get("/api/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True # тк пользователь был доавле ответ должен быть успешный 
    assert data["data"]["id"] == 1 #ид пользовтеля 1
    assert data["data"]["name"] == new_user["name"] #имя совподает с добавленным

#тетс на получение не существующего пользователя
def test_get_user_with_error_id(temp_db):
    with TestClient(app) as client:
        response = client.get("/api/users/2")
    assert response.status_code == 404#бд пустая пожтому при любом ид должен быть стаус 404

#тест удаление пользовтеля
#предварительно очищаем бд и добавляем одного пользователя
def test_delete_user(temp_db, add_user):
    with TestClient(app) as client:
        response = client.delete("/api/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True

#тест на обновление пользователя
#предварительно очищаем бд и добавляем одного пользователя
def test_update_user(temp_db, add_user):
    with TestClient(app) as client:
        response = client.put("/api/users/1", json=update_user)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["id"] == 1
    assert data["data"]["name"] == update_user["name"]#в ответе имя должно совпадать с именем из запроса 
