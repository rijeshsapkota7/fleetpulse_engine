from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///test.db", connect_args={"check_same_thread" : False})

Base = declarative_base()

LocalSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = LocalSession()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()