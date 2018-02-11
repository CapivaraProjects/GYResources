import json
import pytest
from flask import Flask
from app import initialize_app
import models.Logger

app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_log = models.Logger.Logger(type='test',
                                   message='TestMessage',
                                   function="POST",
                                   obs="test",
                                   config="Test")

@pytest.mark.order1
def test_log(generic_log=generic_log):
    resp = client().post('/api/gyresources/logs/', data=str(
        json.dumps(generic_log.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200