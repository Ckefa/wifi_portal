import os
from sqlalchemy import create_engine 
from sqlalchemy.orm import  sessionmaker, declarative_base

from log.logger import getLogger

log = getLogger(__name__)

# Read database uri from env
dbhost = os.getenv("MARIADB_HOST")
dbuser = os.getenv("MARIADB_USER")
dbpasswd = os.getenv("MARIADB_PASSWORD")
dbname = os.getenv("MARIADB_DATABASE")

if not dbhost:
    log.exception("dbhost not set")
    raise Exception("dbhost not set")

if not dbuser:
    log.exception("dbuser not set")
    raise Exception("dbuser not set")

if not dbpasswd:
    log.exception("dbpasswd not set")
    raise Exception("dbpasswd not set")

if not dbname:
    log.exception("dbname not set")
    raise Exception("dbname not set")

dbhost = dbhost.strip()
dbuser = dbuser.strip()
dbpasswd = dbpasswd.strip()
dbname = dbname.strip()

# Creating DB engine from the url
URL = f"mysql+pymysql://{dbuser}:{dbpasswd}@{dbhost}:3306/{dbname}" 
engine = create_engine(url=URL, echo=True) # Declaring the Base for all Table models 
Base = declarative_base()

# Define Database Session
SessionLocal = sessionmaker(bind=engine)

# Create All Tables above
def create_tables():
    Base.metadata.create_all(bind=engine)
    log.info("All Tables created successfully")
