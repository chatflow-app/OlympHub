import os
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

# СЕКРЕТЫ (в реальном проекте хранятся в .env)
SECRET_KEY = "super-secret-key-change-me" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600 # Токен будет жить 10 часов

# Настройка шифрования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
