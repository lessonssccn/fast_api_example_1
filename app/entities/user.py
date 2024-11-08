from app.db.database import Base
from sqlalchemy import TIMESTAMP, Column, String, Boolean, Integer
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    password = Column(String, nullable=False)

    createdAt = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
