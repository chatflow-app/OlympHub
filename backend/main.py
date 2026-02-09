from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from pydantic import BaseModel

# --- НАСТРОЙКИ БАЗЫ ДАННЫХ ---
# Данные берутся docker-compose.yml
DATABASE_URL = "postgresql://admin:olymp_pass@localhost:5432/olymphub_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- МОДЕЛИ БАЗЫ ДАННЫХ (SQLAlchemy) ---

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # Храним хеш, а не чистый пароль
    rating = Column(Integer, default=1000) # Начальный рейтинг R0 = 1000

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    subject = Column(String)
    difficulty = Column(String)
    content = Column(Text)
    correct_answer = Column(String)

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(Integer, ForeignKey("users.id"))
    player2_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    status = Column(String, default="active")
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

# --- БЕЗОПАСНОСТЬ И ВАЛИДАЦИЯ ---

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    password: str

# --- ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ ---

app = FastAPI(title="OlympHub API")

# Создаем таблицы при запуске (если их нет)
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    print("🚀 База данных подключена, таблицы проверены!")

# Получение сессии базы данных для каждого запроса
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ЭНДПОИНТЫ (API) ---

@app.get("/")
def read_root():
    return {"status": "online", "message": "OlympHub API is working"}

@app.post("/register")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Проверка: есть ли уже такой пользователь?
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Такой пользователь уже зарегистрирован")
    
    # Хеширование пароля
    hashed_pwd = pwd_context.hash(user_data.password)
    
    # Сохранение
    new_user = User(username=user_data.username, password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "Пользователь успешно создан",
        "user_id": new_user.id,
        "username": new_user.username
    }