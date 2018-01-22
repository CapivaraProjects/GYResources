const Disease = require('./Disease.js');
const Type = require('./Type.js');

class Image {
	constructor (id=0, disease = Disease(), url = "", description = "", source = "", size = Type()) {
		this.id = id;
		this.disease = disease;
		this.url = url;
		this.description = description;
		this.source = source;
		this.size = size;
	}
}