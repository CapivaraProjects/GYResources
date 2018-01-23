from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class Base:
    engine = None
    Base = declarative_base()
    _SessionFactory = None

    def __init__(self,
                 dbuser="",
                 dbpass="",
                 dbhost="",
                 port="",
                 dbname=""):
        self.engine = create_engine(
                'postgresql://{}:{}@{}:{}/{}'.format(dbuser,
                                                     dbpass,
                                                     dbhost,
                                                     port,
                                                     dbname))
        self._SessionFactory = sessionmaker(bind=self.engine)
        self.Base = declarative_base()

    def session_factory(self):
        self.Base.metadata.create_all(self.engine)
        return self._SessionFactory()
