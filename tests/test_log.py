import json
import pytest
from flask import Flask
from app import initialize_app
import models.Logger

app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_log = models.Logger.Logger(type='testType',
                                   message='TestMessage',
                                   function="POST",
                                   obs="testObs",
                                   config="TEST")

@pytest.mark.order1
def test_log(generic_log=generic_log):
    resp = client().post('/api/gyresources/logs/', data=str(
        json.dumps(generic_log.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp['status_code'] == 201


@pytest.mark.order2
def test_log_emptyRequiredFields(generic_log=generic_log):
    data = {
            "type": "",
            "function": "",
            "config": ""
            }
    resp = client().post('/api/gyresources/logs/', data=str(
        json.dumps(generic_log.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'},
        query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 400

@pytest.mark.order3
def test_log_incorrectFields(generic_log=generic_log):
    data = {
            "type": "",
            "function": "null",
            "config": "unknow"
            }
    resp = client().post('/api/gyresources/logs/', data=str(
        json.dumps(generic_log.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'},
        query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 500