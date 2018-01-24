from sqlalchemy import Column, String, Integer
from capivaraprojects.greeneyes.repository.base import Base


class Text(Base.Base):
    __tablename__ = 'texts'

    id = Column(Integer, primary_key=True)
    language = Column(String(2000))
    tag = Column(String(2000))
    value = Column(String(2000))
    description = Column(String(2000))

    def __init__(self, id, language, tag, value, description):
        self.id = id
        self.language = language
        self.tag = tag
        self.value = value
        self.description = description
