from sqlalchemy import Column, String, Integer, ForeignKey
from capivaraprojects.greeneyes.repository.base import Base


class User(Base.Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    idType = Column('id_type', Integer, ForeignKey('types.id'))
    email = Column(String(200))
    username = Column(String(20))
    password = Column(String(128))
    salt = Column(String(32))
    dateInsertion = Column('date_insertion', String(100))
    dateUpdate = Column('date_last_update', String(100))

    def __init__(self,
                 id,
                 idType,
                 email,
                 username,
                 password,
                 salt,
                 dateInsertion,
                 dateUpdate):
        self.id = id
        self.idType = idType
        self.email = email
        self.username = username
        self.password = password
        self.salt = salt
        self.dateInsertion = dateInsertion
        self.dateUpdate = dateUpdate
