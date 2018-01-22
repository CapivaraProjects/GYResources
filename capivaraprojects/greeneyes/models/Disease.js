const Plant = require('./Plant.js');

class Disease {
	constructor (id=0, plant=Plant, scientificName="", commonName="", images=list()) {
		this.id = id;
		this.plant = plant;
		this.scientificName = scientificName;
		this.commonName = commonName;
		this.images = images;
	}
}