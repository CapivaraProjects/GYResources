from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from capivaraprojects.greeneyes.database.Disease import Disease
from capivaraprojects.greeneyes.repository.base import Base


class Plant(Base.Base):
    __tablename__ = 'plants'

    id = Column(Integer, primary_key=True)
    scientificName = Column('scientific_name', String(2000))
    commonName = Column('common_name', String(2000))
    diseases = relationship('Disease',
                            back_populates='plant')

    def __init__(self, id, scientificName, commonName, diseases):
        self.id = id
        self.scientificName = scientificName
        self.commonName = commonName
        self.diseases = diseases
