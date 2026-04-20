from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from resources.db_creds import MoviesDbCreds

USERNAME = MoviesDbCreds.DB_USER
PASSWORD = MoviesDbCreds.DB_PASSWORD
HOST = MoviesDbCreds.DB_HOST
PORT = MoviesDbCreds.DB_PORT
DATABASE_NAME = MoviesDbCreds.DB_NAME

# движок для подключения к бд
engine = create_engine(
    f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}",
    echo=False # Сделать True если нужна будет откладка SQL-request
)

SessionLocal = sessionmaker(bind=engine)

def get_db_session():
    """Создает новую сессию в бд"""
    return SessionLocal()