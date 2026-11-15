
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

app = FastAPI(title="JWT Authentication API")

SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

users_db = {}
items_db = {}

class UserCreate(BaseModel):
    username: str
    password: str

class Item(BaseModel):
    name: str
    description: str

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        username = payload.get("sub")
        if username not in users_db:
            raise HTTPException(status_code=401, detail="Invalid user")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/")
def home():
    return {"message": "FastAPI JWT Authentication API"}

@app.post("/register")
def register(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    users_db[user.username] = hash_password(user.password)
    return {"message": "User registered successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    hashed = users_db.get(form_data.username)
    if not hashed or not verify_password(form_data.password, hashed):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me")
def read_users_me(username: str = Depends(get_current_user)):
    return {"username": username}

@app.post("/items")
def create_item(item: Item, username: str = Depends(get_current_user)):
    item_id = len(items_db) + 1
    items_db[item_id] = item.dict()
    return {"id": item_id, "owner": username, **items_db[item_id]}

@app.get("/items")
def get_items(username: str = Depends(get_current_user)):
    return items_db

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item, username: str = Depends(get_current_user)):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[item_id] = item.dict()
    return {"message": "Item updated", "item": items_db[item_id]}

@app.delete("/items/{item_id}")
def delete_item(item_id: int, username: str = Depends(get_current_user)):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    return {"message": "Item deleted"}
