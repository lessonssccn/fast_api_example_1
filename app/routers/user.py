# самый фажный файл проекта сожержит фукции обработки запросво
# в пакете app.routers могут находиться и другие файлы для обработки других групп запросво
# здесь обрабатываются только запросы для работы с таблицей users и связанных с ней
# здесь реализован базовый crud
#create - созадание 
#read - чтение 2 варианта для списка и для одиночной записи
#update - обновление поменять имя или парль или то и то
#delete - удаления по ил
from app.entities.user import User #импоркт сущности для взаимодейсвия с бд 
import app.models.user as user_models #импорт моделей для типисазии запросов и ответов
from app.models.base import SuccessResponse, UnsuccessResponse #импорт типовых моделей для тех же целей
from sqlalchemy.orm import Session # импорт для типизаииц параметров функции
from fastapi import Depends, status, APIRouter, Response, Path # дополнительный функционал из fastapi
from app.db.database import get_db #импорт функции для создания бд сессии

#/api/users - в файле main настроен перфикс к этой группе эндпоинтов
router = APIRouter() # создаем обект который будет определять какую функцию запустить при том или ином запросе


#обрабатываем запрос на создание пользователя
#ожидаем POST запрос с путем /api/users 
#при успехе возвращем код 201, а в теле ответа UserResponse описан в файле app.models.user
#не коректной опбраотки не предполагается если данные в теле запроса соответсуют моделе AddUser тоже из файла app.models.user
#интересен пример использования db: Session = Depends(get_db)
#при звпуске функции add_user будет запущена функция get_db котрая создаст обект Session через который будет проходить вся работа с бд
@router.post("/", status_code=status.HTTP_201_CREATED, response_model = user_models.UserResponse)
def add_user(payload: user_models.AddUser, db: Session = Depends(get_db)):# функция получает сессию (db) как зависсимость и тело запорса в параметре payload 
    new_user = User(**payload.model_dump()) # model_dump возвращает словарь где ключи именна полей из модели а значения то что указал пользователь
                                            # **payload.model_dump() разбиваем соварь на отдельнные именнованные аргументы при вызове конструктора
                                            # User - тем самым создавая обект класса который испольуется orm sqlalchemy 
    db.add(new_user) # добавляем запись в бд, пофакту запись еще не добавленна тк мы не сделали коммит, тоесть не провели фиксацию изменений
    db.commit()#фиксируем изменения
    db.refresh(new_user) #обновляем объект точнее значение его полей, нам нужна дата и ид 

    user = user_models.User(id = new_user.id, name = new_user.name, createdAt = new_user.createdAt) #из моедли для бд созадем моедль для ответа пользователю
    return user_models.UserResponse(data = user)#завершаем формировани ответа пользователю и возвращаем ответ
    # все остальные преобразования и формирования http пакета берет на себя fastapi 
    # похорошему весь этот код должен находиться не злесь и разбит на дополнительные функции, но для простоты оставляю его так
    # очень важно возвращять из функции либо примитивы либо обеекты классов унаследованных от BaseModel т.к. у них есть
    # удобное преобазование в json которое и использует fastapi 


#получение пользователя по ид
#запрос с вариативной частью пути, в данном случае с коечной частью
#/api/users/{id}
#{id} - щаблон изменяемой части
#ждем замето {id} целое число, иначе до вызова  get_user_by_id дело не дайдет сам fastapi проверит тип и если что-то не то 
#сгенириует ответ о не соответсвии типа 
#реагируем только на GET запросы остальные запросы либо поподаю в другие функции как пример DELETE/PUT 
#либо гененрирую ошибку 405 - метод не поддерживается 
#поумолчанию возвращеме ответ с кодом 200
#если юзер найде и тело ответа UserResponse
#если передан отрицательный id возвращеаем код ответа 400 сделанно для демо
#и UnsuccessResponse в теле  UnsuccessResponse содержит заполенный error о том что id не коектен
#если юзера с указнным id найти не удалось то код ответа 404
#в теле ответа UnsuccessResponse c error User not found 
#интересен параметр id: int = Path() указывающь что надо брать значение id из пути
#и параметр response: Response позволяющий менять статус код отвтеа 
@router.get("/{id}", status_code= status.HTTP_200_OK, response_model = user_models.UserResponse | UnsuccessResponse)
def get_user_by_id(response: Response, id: int = Path(), db: Session = Depends(get_db)):
    if id < 1: #если переданный id меньше еденицы считаем его не коректным хотя можно было просто поскать по нему в бд и ничего не неайти
                #у нас есть гарантия что он уже целое число fastapi проверяет тип по анотациям укзаным после : у параметров функции 
                # иные варианты отвергаются ифункция не будет запущена  
        response.status_code = 400 #меняем статус код на 400
        return UnsuccessResponse(error=f"Incorrect id = {id}") #формируем ответ и возвращем его 
    
    user_db = db.query(User).filter_by(id = id).first() #берем в бд одну запись с совподающим ид, они унас уникалны 

    if not user_db: #если ничего не найдено 
        response.status_code = 404 #выставляем код ответа в 404
        return UnsuccessResponse(error=f"User not found by id = {id}")#формируем ответ

    user = user_models.User(id = user_db.id, name = user_db.name, createdAt = user_db.createdAt) #из модели для бд формируем модель для ответа клиенту
    return user_models.UserResponse(data = user) #завершаем формирование ответа

#для получения списка пользователей
#тк пользователей может быть много добавляем возможность получить только их часть укзав смещени от начала списка иколичество
#limit - сколько пользователей вернуть если столько нет вернет меньше
#offset - смещение от начала сиписка начинается от 0 
#GET запрос c параметами необязательными в отличии от изменяемой части (пример запроса выше) пути параметры носят опициональный характер
#их можно не передвать, здесь если их не передать то у них будет значение по умолчанию limit:int = 10, offset:int = 0
#если передавать то ожидается передача int иначе ошибка валидации и функци не будет запущенна
#вслучае коректности пораметров будет возвращен статус 200 и в теле ListUserResponse
#при не коректных значениях параметров статус 400 и в теле UnsuccessResponse
@router.get("/", status_code=status.HTTP_200_OK, response_model = user_models.ListUserResponse | UnsuccessResponse)
def get_user_by_id(response: Response, limit:int = 10, offset:int = 0, db: Session = Depends(get_db)):
    if limit <= 0:# лимит должен быт строго больше нуля инача некоректно 
        response.status_code = 400
        return UnsuccessResponse(error="limit must be positive int")
    
    if limit >1000: #лимит строго меньше 1000 иначе некоректно
        response.status_code = 400
        return UnsuccessResponse(error="limit must be < 1000")

    
    if offset < 0: #сдвиг 0 и больше потолка нет
        response.status_code = 400
        return UnsuccessResponse(error="limit must be offset int or zero")


    list_user_db = db.query(User).limit(limit).offset(offset).all()#получаем из бд limit записей со смещением 
    #преобразуем все полученные записи к моделям User для возврата клиенту
    list_user = list(map(lambda user_db: user_models.User(id = user_db.id, name = user_db.name, createdAt = user_db.createdAt), list_user_db))
    return user_models.ListUserResponse(items = list_user, offset=offset, limit=limit) #заврешаем формирование ответа 
                                                                                       #и заполняем значение offset и limit 
                                                                                       #тем же что передал клиент, 
                                                                                       #чтобы он мог отследить достиг он конца списка 
                                                                                       #и на какой запрос получил ответ 


#удаление пользователя по id 
#очень похож на поис пользователя по id но не возращает информацию о пользователе а удает его и возвращает SuccessResponse при успехе
#DELETE метод
@router.delete("/{id}", status_code=status.HTTP_200_OK, response_model = SuccessResponse | UnsuccessResponse)
def delete_user(response: Response, id: int = Path(), db: Session = Depends(get_db)):
    if id < 1:
        response.status_code = 400
        return UnsuccessResponse(error=f"Incorrect id = {id}")
    
    user_db = db.query(User).filter_by(id = id).first()

    if not user_db:
        response.status_code = 404
        return UnsuccessResponse(error=f"User not found by id = {id}")
    
    db.delete(user_db)#удаление пользовталея
    db.commit()#фиксация изменений в бд

    return SuccessResponse()

#изменение полтзователя 
#PUT метод
#в пути надо передать ид изменяемого пользователя сам ид не подлежит смене иначе нарушим целостность данных
@router.put("/{id}", status_code=status.HTTP_200_OK, response_model = user_models.UserResponse | UnsuccessResponse)
def update_user(response: Response, payload: user_models.UpdateUser, id: int = Path(), db: Session = Depends(get_db)):
    if id < 1:
        response.status_code = 400
        return UnsuccessResponse(error=f"Incorrect id = {id}")
    
    user_db = db.query(User).filter_by(id = id).first()

    if not user_db:
        response.status_code = 404
        return UnsuccessResponse(error=f"User not found by id = {id}")

    #анализ тела запроса тк было позвоенно передать оба не заполенных поля
    #нужны проверки на то что заполенно
    #если не заполенно оба поля то сообщаем о некоректности запроса
    if not payload.name and not payload.password:
        response.status_code = 400
        return UnsuccessResponse(error=f"Incorrect payload name or password must be determined")
    
    if payload.name:
        user_db.name = payload.name
    if payload.password:
        user_db.password = payload.password
    
    
    db.commit()#фиксируем измения 
    db.refresh(user_db)#подтягиваем их в объект

    user = user_models.User(id = user_db.id, name = user_db.name, createdAt = user_db.createdAt)
    return user_models.UserResponse(data = user)


