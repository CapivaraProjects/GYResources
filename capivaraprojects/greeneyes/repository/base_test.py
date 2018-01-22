from capivaraprojects.greeneyes.repository.base import Base
from capivaraprojects.greeneyes.database.Plant import Plant
from capivaraprojects.greeneyes.database.Disease import Disease
from capivaraprojects.greeneyes.database.Type import Type
from capivaraprojects.greeneyes.database.Image import Image


def test_connection():
    base = Base('capivara',
                'test',
                '127.0.0.1',
                '5432',
                'green_eyes')
    session = base.session_factory()
    image_query = session.query(Image)
    session.close()
    assert type(image_query.all()) == list
