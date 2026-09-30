from fastapi import APIRouter,Depends,HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from typing import Annotated
from database import sessionlocal
from router.auth import get_current_user
from models import Todos

router = APIRouter()


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]


@router.get('/admin/todo')
def read_all(user : user_dependency, db : db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401,detail="Failed Authentication")
    return db.query(Todos).all()

@router.delete('/admin/delete/{todo_id}')
def delete_todos(user : user_dependency,db : db_dependency,todo_id : int):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401,detail="Failed Authentication")
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail='to do not found')
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
    return JSONResponse(status_code=201,content={'message ': 'to do deleted successfully'})

