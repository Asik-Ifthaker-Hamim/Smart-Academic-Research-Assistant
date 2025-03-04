from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
from app.db.session import get_db

class CustomBase:
    
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

Base = declarative_base(cls=CustomBase)

__all__ = ['Base', 'get_db']
