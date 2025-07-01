from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import logging
from typing_extensions import Annotated, Union
from pydantic import BaseModel
import schemas
import models
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import database
from pydantic import parse_obj_as


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# fake_users_db = {
#     "johndoe": {
#         "id": 1,
#         "username": "johndoe",
#         "full_name": "John Doe",
#         "email": "johndoe@example.com",
#         "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", #secret
#         "disabled": False,
#     }
# }

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None

'''
function that verifies if the hashed_password in DB is same as the password inputed by user
'''
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

'''
returns hash of password string
'''
def get_password_hash(password):
    return pwd_context.hash(password)

'''
takes username as input and returns DBUser object if username present in db
'''
def get_user(db : Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        logger.debug(f"get_user() check for username present in db : {user.username}")
        pydantic_DBuser = parse_obj_as(schemas.DBUser, user)
        return pydantic_DBuser 

'''
Takes input username and password given by user and then verifies the credentials and returns the DBUser Object.
'''
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hash_password):
        return False
    return user

'''
Function that takes a dict 'data' and expires_delta and creates jwt token that encodes the data dict and sets the expiry to expires_delta
'''
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

'''
Get current user from jwt token. Returns DBUser object.
'''
#Annotated[str, Depends(oauth2_scheme)]
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(database.get_db)):
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
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# '''
# Users have a field called disabled which is of type Boolean. If the user is logged in then it will True otherwise False.
# '''
# async def get_current_active_user(
#     current_user: Annotated[schemas.UserBase, Depends(get_current_user)],
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user



'''
Checks if user credentials are correct and then returns access token. This is the URL path that the frontend will hit to get access code.
'''
@router.post("/token")
async def login_for_access_token(user_cred: schemas.UserLogin, db: Session = Depends(database.get_db)) -> Token:
    logger.debug(user_cred)
    user = authenticate_user(db, user_cred.username, user_cred.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")



@router.get("/current_user", response_model=schemas.DBUser)
async def get_curr_user(current_user: Annotated[schemas.DBUser, Depends(get_current_user)]):
    return current_user


# # TEST

# @router.get("/test/users/me/items/")
# async def read_own_items(
#     current_user: Annotated[schemas.UserBase, Depends(get_current_active_user)],
# ):
#     return [{"item_id": "Foo", "owner": current_user.username}]
