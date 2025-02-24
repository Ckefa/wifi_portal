from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy.types import DATETIME, Float, String
from db.db import Base

class User(Base):
    """
    This is the Users Table
    """
    __tablename__ = "users"  # optional pluralization

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    phone = Column(String(30), unique=True, nullable=False)
    package = Column(String(30))
    amount = Column(Float, default=0.00)
    status = Column(String(10), default="expired")
    expiry = Column(DATETIME, default=datetime.now)
    total = Column(Float, default=0.00)

    def __init__(self, phone, package=None):
        self.phone = phone
        self.package = package
        # expiry defaults to datetime.now() via column default; override if needed
        # id is set automatically via default

    def check_status(self) -> bool:
        """
        Check the user's status based on package and expiry.
        Returns True if the user has a package and it has not expired.
        """
        try:
            print(f'Checking status: {self.__dict__.items()}')
            if self.package is None or self.expiry < datetime.now():
                return False
            return True
        except Exception as e:
            print(f"Error checking status: {e}")
            return False

    def save(self, session) -> bool:
        """
        Add and commit this user to the database.
        """
        try:
            session.add(self)
            session.commit()
            print("User Details Updated")
            return True
        except Exception as e:
            session.rollback()
            print(f"Error saving changes to database: {e}")
            return False

    @classmethod
    def get_or_create(cls, phone, session, package=None):
        """
        Retrieve a user by phone, or create one if it doesn't exist.
        """
        try:
            user = session.query(cls).filter(cls.phone == phone).first()
            if user:
                return user, False
            user = cls(phone, package)
            session.add(user)
            session.commit()
            return user, True
        except Exception as e:
            session.rollback()
            print(f"Error in get_or_create: {e}")
            raise

