from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost/bookweb_db"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("Подключение к базе данных успешно!")
except Exception as e:
    print(f"Ошибка подключения к базе данных: {e}")
