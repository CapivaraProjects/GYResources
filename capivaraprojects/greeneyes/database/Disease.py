from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from capivaraprojects.greeneyes.database.Image import Image
from capivaraprojects.greeneyes.repository.base import Base


class Disease(Base.Base):
    __tablename__ = 'diseases'

    id = Column(Integer, primary_key=True)
    scientificName = Column('scientific_name', String(2000))
    commonName = Column('common_name', String(2000))
    idPlant = Column('id_plant', Integer, ForeignKey('plants.id'))
    plant = relationship('Plant', back_populates='diseases')
    images = relationship('Image', back_populates='disease')

    def __init__(self, id, scientificName, commonName, idPlant, plant):
        self.id = id
        self.scientificName = scientificName
        self.commonName = commonName
        self.idPlant = idPlant
        self.plant = plant
