from flask import Flask

class BaseResponse:

	def __init__(self, status_code=0, message="", elapsed_ms=0.0, response=Flask.response_class):
		self.status_code = status_code
		self.message = message
		self.elapsed_ms = elapsed_ms
		self.response = response
