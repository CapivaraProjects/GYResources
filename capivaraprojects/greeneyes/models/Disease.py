from capivaraprojects.greeneyes.models.Plant import Plant
class Disease:
    def __init__(self, id=0, plant=Plant(), scientificName="", commonName="", images=list()):
        self.id = id
        self.plant = plant
        self.scientificName = scientificName
        self.commonName = commonName
        self.images = images
