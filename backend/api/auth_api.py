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
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15 #minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60#days

if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable not set!")

if not REFRESH_SECRET_KEY:
    raise ValueError("REFRESH_SECRET_KEY environment variable not set!")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

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
    user = db.query(schemas.User.User).filter(schemas.User.User.username == username).first()
    if user:
        logger.debug(f"get_user() check for username present in db : {user.username}")
        pydantic_DBuser = parse_obj_as(models.User.DBUser, user)
        return pydantic_DBuser 


'''
Takes input username and password given by user and then verifies the credentials and returns the DBUser Object.
'''
def authenticate_user(db : Session, username: str, password: str):
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
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



async def get_current_user(request: Request):
    try:
        logger.debug("Request cookies:", request.cookies)  
        token = request.cookies.get("access_token")  # Retrieve token from cookies
        
        if not token:
            logger.debug("Token is missing")
            raise HTTPException(status_code=401, detail="Token is missing")
        
        # Decode the token without the 'Bearer' prefix
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": True})
                
        username: str = payload.get("sub")  # Extract the username
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        
        return username

    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        logger.error(f"JWT Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    

async def verify_current_user(request: Request):
    try:
        # logger.debug("Request cookies: %s", request.cookies)  
        token = request.cookies.get("access_token")  # Retrieve access token from cookies
        refresh_needed = False
        username = ""
        
        if not token:
            logger.debug("Access token is missing, refresh needed")
            refresh_needed = True
        else:
            # Decode the access token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": True})
            username: str = payload.get("sub")  # Extract the username
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid access token",
                )
            
            exp_timestamp = payload.get("exp")  
            expiration_time = datetime.utcfromtimestamp(exp_timestamp)
            current_time = datetime.utcnow()
            time_remaining = expiration_time - current_time
            
            logger.debug("Token expires in: %s", time_remaining)

        # refresh_needed = time_remaining < timedelta(minutes=5)
        if refresh_needed or time_remaining < timedelta(minutes=5):
            logger.info("Checking refresh token for username: %s", username)
            
            refresh_token = request.cookies.get("refresh_token")
            if not refresh_token:
                logger.warning("Refresh token is missing")
                # User stays logged in despite missing refresh token
                return {"refresh": False, "authenticated": False, "username": username, "message": "Refresh token is missing"}
            
            try:
                refresh_payload = jwt.decode(
                    refresh_token, 
                    REFRESH_SECRET_KEY, 
                    algorithms=[ALGORITHM], 
                    options={"verify_exp": True}
                )
                refresh_username: str = refresh_payload.get("sub")
                
                # if refresh_username != username:
                #     logger.warning("Refresh token does not match access token username")
                #     return {"refresh": False, "username": username, "message": "Refresh token mismatch"}
                
                # If refresh token is valid, return a response indicating refresh is possible
                logger.info("Refresh token is valid for username: %s  || request to refresh access token sent", refresh_username)
                return {"refresh": True, "authenticated": True, "username": refresh_username, "message": "Token can be refreshed"}
            
            except jwt.ExpiredSignatureError:
                logger.warning("Refresh token has expired")
                return {"refresh": False, "authenticated": False, "username": username, "message": "Refresh token expired"}
            except JWTError as e:
                logger.warning(f"Refresh token error: {e}")
                return {"refresh": False, "authenticated": False, "username": username, "message": "Invalid refresh token"}
        
        # Token is still valid and does not need refreshing
        return {"refresh": False, "authenticated": True, "username": username, "message": "Access token is valid"}

    except jwt.ExpiredSignatureError:
        logger.error("Access token has expired, refresh request sent...")
        # Refreshing access token
        return {"refresh": True, "username": payload.get("sub"), "message": "Access token expired, refreshing..."}   
    
        
        # raise HTTPException(status_code=401, detail="Access token has expired")
    except JWTError as e:
        logger.error(f"JWT Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid access token")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def create_refresh_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Verify tokens
def verify_refresh_token(request: Request):
    try:
        logger.debug("Request cookies:", request.cookies)  
        token = request.cookies.get("refresh_token")  # Retrieve token from cookies
        
        if not token:
            logger.debug("Token is missing")
            raise HTTPException(status_code=401, detail="RefreshToken is missing")
        
        # Decode the token without the 'Bearer' prefix
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": True})
                
        username: str = payload.get("sub")  # Extract the username
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        
        return username

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )


'''
Checks if user credentials are correct and then returns access token. This is the URL path that the frontend will hit to get access code.
'''
@router.post("/token")
async def login_for_access_token(user_cred: models.User.UserLogin, db: Session = Depends(database.get_db)) -> JSONResponse:
    logger.debug("user_cred : " ,user_cred)
    user = authenticate_user(db, user_cred.username, user_cred.password)
    logger.debug("user : ", user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
     )
    
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=f"{access_token}",
        httponly=True,       # Prevent JS access
        secure=False,         # Send only over HTTPS if True
        samesite="Strict",   # Prevent CSRF
        expires=datetime.now(timezone.utc)  + access_token_expires, #15 minutes
        path="/",            # Apply cookie to all paths
    )
    response.set_cookie(
        key="refresh_token",
        value=f"{refresh_token}",
        httponly=True,       # Prevent JS access
        secure=False,         # Send only over HTTPS if True
        samesite="Strict",   # Prevent CSRF
        expires=datetime.now(timezone.utc) + refresh_token_expires, #7 days
        path="/",            # Apply cookie to all paths
    )
    
    print(f"access_token generated : {access_token}")
    
    return response


@router.post("/refresh_token")
def refresh_token(username: str = Depends(verify_refresh_token)) -> JSONResponse:
    
    new_access_token = create_access_token({"sub": username}) # create new access token
    
    # Set the new access token in the cookie
    response = JSONResponse(content={"message": "Access token refreshed"})
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    response.set_cookie(
        key="access_token",
        value=f"{new_access_token}",
        httponly=True,       # Prevent JS access
        secure=False,         # Send only over HTTPS if True
        samesite="Strict",   # Prevent CSRF
        expires=datetime.now(timezone.utc)  + access_token_expires, #15 minutes
        path="/",            # Apply cookie to all paths
    )
    
    return response



@router.post("/verify_token")
async def verify_token(data = Depends(verify_current_user)):
    return data


@router.post("/logout")
async def logout(request: Request) -> JSONResponse:
    cookies = request.cookies
    print("\n\nCurrent Cookies:", cookies)  # Debugging output
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


    

@router.get("/current_user", response_model=models.User.DBUser)
async def get_curr_user(current_user: Annotated[models.User.DBUser, Depends(get_current_user)]):
    return current_user
