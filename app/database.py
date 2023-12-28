from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings


# 'driver_name://<username>:<password>@<ip-address:port/db>'
SQLALCHEMY_DATABASE_URL = (f"{settings.driver_name}://{settings.database_username}:{settings.database_password}@"
                           f"{settings.database_hostname}:{settings.database_port}/{settings.database_name}")

# The Engine is responsible for sqlalchemy to connect to postgres
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    # The session obj is responsible for talking to the db. Every time we get a request we get a session and after the
    # request is done, we'll then close it out.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# connecting directly to SQL without using sqlalchemy
# import psycopg
# from psycopg.rows import dict_row
# import time
#
# while True:
#     try:
#         conn = psycopg.connect(
#             host='localhost',
#             dbname='fastapi',
#             port=5433,
#             user='postgres',
#             password='rVwQi6bKjjrDNqdpdxJz',
#             row_factory=dict_row    # to generate rows as dictionaries in psycopg3 is by passing the dict_row row factory
#         )
#
#         cursor = conn.cursor()
#         print("Database connection was successful")
#         break
#
#     except Exception as error:
#         print("Connecting to database failed")
#         print("Error: ", error)
#         time.sleep(3)

