from sqlalchemy import Column, String, Integer
from capivaraprojects.greeneyes.repository.base import Base


class Type(Base.Base):
    __tablename__ = 'types'

    id = Column(Integer, primary_key=True)
    value = Column('scientific_name', String(2000))
    description = Column('common_name', String(2000))

    def __init__(self, id, value, description):
        self.id = id
        self.value = value
        self.description = description
