from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import SessionLocal, engine
from auth_utils import hash_password

# Создаем таблицы (SQLAlchemy проверит models.py и создаст users и tasks)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="OlympHub API")

# Зависимость для БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "online", "message": "OlympHub API is working"}

# --- ПОЛЬЗОВАТЕЛИ ---

@app.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Проверка на существование
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Хеширование и сохранение
    hashed_pwd = hash_password(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- ЗАДАЧИ ---

@app.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()

@app.post("/tasks")
def create_task(task_data: schemas.TaskCreate, db: Session = Depends(get_db)):
    # Мы предполагаем, что ты добавил TaskCreate в schemas.py
    new_task = models.Task(**task_data.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"message": "Задача добавлена", "id": new_task.id}