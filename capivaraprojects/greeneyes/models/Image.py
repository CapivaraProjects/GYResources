from capivaraprojects.greeneyes.models.Disease import Disease
from capivaraprojects.greeneyes.models.Type import Type
class Image:
    def __init__(self, 
            id=0, 
            disease=Disease(), 
            url="", 
            description="", 
            source="", 
            size = Type()):
        self.id = id
        self.disease = disease
        self.url = url
        self.description = description
        self.source = source
