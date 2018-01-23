from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from capivaraprojects.greeneyes.repository.base import Base


class Image(Base.Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    url = Column(String(2000))
    description = Column(String(2000))
    source = Column(String(2000))
    size = Column(Integer, ForeignKey('types.id'))
    idDisease = Column('id_disease', Integer, ForeignKey('diseases.id'))
    disease = relationship('Disease', back_populates='images')

    def __init__(self,
                 id,
                 url,
                 description,
                 source,
                 size,
                 idDisease,
                 disease):
        self.id = id
        self.url = url
        self.description = description
        self.source = source
        self.size = size
        self.idDisease = idDisease
        self.disease = disease
