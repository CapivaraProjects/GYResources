from capivaraprojects.greeneyes.models.Type import Type

class User:
	def __init__(self, 
		id = 0, 
		email = "", 
		username = "", 
		password = "", 
		salt = "", 
		type = Type(), 
		date_insertion = "", 
		date_update = ""):
		
		self.id = id
		self.email = email
		self.username = username
		self.password = password
		self.salt = salt
		self.type = type
		self.date_insertion = date_insertion
		self.date_update = date_update