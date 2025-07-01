from fastapi import APIRouter, Depends, HTTPException, status
import logging
from typing_extensions import Annotated, Union
import schemas
import models
from passlib.context import CryptContext
from api.auth_api import pwd_context
from sqlalchemy.orm import Session
import database
from pydantic import parse_obj_as
import traceback


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/user",
    tags=["user"],
    responses={404: {"description": "Not found user_api"}},
)



'''
Signup User
'''
@router.post('/signup', status_code=status.HTTP_201_CREATED)
def signup_user(new_user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    print(f"new_user : {new_user}\n\n")
    try:
        hashed_password = pwd_context.hash(new_user.password)
        new_user_json = new_user.dict();
        new_user_json['hash_password'] = hashed_password
        new_user_json.pop('password')
        user_db = models.User(**new_user_json)
        # user_db.hashed_password = hashed_password
        db.add(user_db)
        db.commit()
        pydantic_DBuser = parse_obj_as(schemas.DBUser, user_db)
        return pydantic_DBuser
    except Exception as e:
            db.rollback()  # Rollback the transaction in case of error
            traceback.print_exc()  # Print the stack trace
            if('Duplicate entry' in str(e)):
                print("Duplicate Entry")
                return {"error" : "Username or Email already taken, please choose a different username or login"}
            
            return {"error" : f"Error occured during User Creation in DB : {e}"}
        


# '''
# Login User
# '''
# @router.post('/login')
# def login_user(user_cred: schemas.UserLogin, db: Session = Depends(database.get_db)):
#     try:
#         return {"Login Atempt" : "Success"}
#     except Exception as e:
#         db.rollback()
#         traceback.print_exc() 
#         return {"error" : f"Error occured during User Login: {e}"} 

    
@router.get('/test1')
def test1():
    return {'test':'success'}