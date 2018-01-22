const Type = require('./Type.js');

class User {
	constructor (id = 0, email = "", username = "", password = "", salt = "", type = Type(), date_insertion = "", date_update = "") {
		this.id = id;
		this.email = email;
		this.username = username;
		this.password = password;
		this.salt = salt;
		this.type = type;
		this.date_insertion = date_insertion;
		this.date_update = date_update;
	}
}