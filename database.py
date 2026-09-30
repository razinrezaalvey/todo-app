from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
# engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={'check_same_thread': False})

# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:alvey@localhost/todoapplicationdatabase'
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:12345678@127.0.0.1:3306/todoapplicationdatabase'
engine = create_engine(SQLALCHEMY_DATABASE_URL)


sessionlocal = sessionmaker(autoflush=False,autocommit= False,bind=engine)

Base = declarative_base()