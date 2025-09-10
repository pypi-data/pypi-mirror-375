from dataclasses import dataclass
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


@dataclass
class Config_db:
    dbms: str
    username: str
    password: str
    ip: str
    port: int
    database_name: str

def get_db(config: Config_db):
    database_url = f"{config.dbms}://{config.username}:{config.password}@{config.ip}:{str(config.port)}/{config.database_name}"
    engine = create_engine(database_url, pool_pre_ping=True, pool_recycle=3600)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e