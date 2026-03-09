from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

import models
import schemas
from database import SessionLocal, engine
from auth_utils import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="OlympHub API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для получения текущего пользователя по токену
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
def read_root():
    return {"status": "online", "message": "OlympHub API is working"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()

@app.post("/tasks")
def create_task(task_data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Мы берем id из текущего пользователя, которого определили по токену
    new_task = models.Task(
        title=task_data["title"],
        description=task_data["description"],
        owner_id=current_user.id  # Вот здесь магия связи!
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task