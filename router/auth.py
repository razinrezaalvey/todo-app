from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from models import Users
from datetime import timedelta,datetime,timezone
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from sqlalchemy.orm import session
from typing import Annotated,Optional
from database import sessionlocal
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
router = APIRouter()    
from jose import jwt

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth_bearer = OAuth2PasswordBearer(tokenUrl='login')
SECRET_KEY = '23aabf0adff4799780d2056bc2b9fee16fa692cac71c101c449acdc8b506aacf'
ALGORITHM = 'HS256'

class Createuser(BaseModel):
    email : str
    username : str
    firstname : str
    lastname : str
    password : str
    role : str
    phone_number : str

class update_user(BaseModel):
    email : Optional[str] = Field(default=None)
    username : Optional[str] = Field(default=None)
    firstname : Optional[int] = Field(default=None)
    lastname : Optional[bool] =Field(default=None)
    phone_number : Optional[str] = Field(default=None)

class update_password(BaseModel):
    current_password : str
    new_password : str

def authenticate_user(username,password,db):
    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        return False
    if bcrypt_context.verify(password,user.hash_password):
        return user
    return False

def create_access_token(username:str,user_id:int,role:str, expires_delta:timedelta):
    encode = {'sub':username,'id':user_id,'role':role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp' : expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

def get_current_user(token:Annotated[str,Depends(oauth_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username : str = payload.get('sub')
        user_id : int = payload.get('id')
        role : str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=404,detail='user not found')
        return {'username':username,'id':user_id,'role':role}
    except:
        raise HTTPException(status_code=404,detail='user not found')

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]

@router.post('/createuser')
def create_users(db:db_dependency, new_user : Createuser):
    user_model = Users(
        email = new_user.email,
        username = new_user.username,
        firstname = new_user.firstname,
        lastname = new_user.lastname,
        hash_password = bcrypt_context.hash(new_user.password),
        is_active = True,
        role = new_user.role,
        phone_number = new_user.phone_number
    )
    db.add(user_model)
    db.commit()

    return JSONResponse(status_code=201,content={'message ': 'User created successfully'})

@router.post('/login')
def login_user(db : db_dependency,from_data : Annotated[OAuth2PasswordRequestForm,Depends()]):
    user = authenticate_user(from_data.username, from_data.password,db)
    if not user:
        return JSONResponse(status_code=400,content='Failed authentication')

    token = create_access_token(user.username,user.id,user.role, timedelta(minutes=30))
    return {'access_token' : token,'token_type' : 'bearer'}



@router.put('/edituser')
def edit_user(user : user_dependency,db : db_dependency,edit_user : update_user):
    if user is None:
        raise HTTPException(status_code=401,detail="Failed Authentication")
    usertable = db.query(Users).filter(Users.id == user.get('id')).first()
    
    update_data = edit_user.model_dump(exclude_unset=True)
    for key,value in update_data.items():
        setattr(usertable,key,value)
    db.commit()
    return JSONResponse(status_code=201,content={'message ': 'user updated successfully'})


@router.put('/passwordchange')
def edit_password(user : user_dependency,db : db_dependency,edit_password : update_password):
    if user is None:
        raise HTTPException(status_code=401,detail="Failed Authentication")
    user = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(edit_password.current_password,user.hash_password):
        raise HTTPException(status_code=401,detail="wrong password")
    user.hash_password = bcrypt_context.hash(edit_password.new_password)
    db.add(user)
    db.commit()
    
    return JSONResponse(status_code=201,content={'message ': 'password updated successfully'})

