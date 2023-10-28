from flask import Flask
from flask import render_template
from flask import request
from markupsafe import escape
import uuid
import datetime

app = Flask(__name__)

memory = {}

# @app.get("/")
# #@app.get('/hello/<str:name>')
# def render_index(name=None):
#     return render_template('index.html', name={escape(name)})


@app.get("/")
@app.get("/:subject_id")
def render_index():
    if request.args.get('subject_id'):
        subject_id = request.args.get('subject_id')
        if memory.get(subject_id):
            return {"nb_options": memory[subject_id]['nb_options']}
        return '<h1>Wrong subjectId</h1>'
    return render_template('index.html')


@app.errorhandler(404)
def not_found():
    return render_template('error.html'), 404


@app.post('/generate-qr-code')
def number_of_options():
    if request.json.get('nb_options'):
        survey_id = uuid.uuid4().hex
        memory[survey_id] = {}
        memory.get(survey_id)['created_date'] = datetime.datetime.now()
        memory.get(survey_id)['nb_options'] = request.json.get('nb_options')        
        return survey_id
    return '<h1>Number of options not given</h1>'

    
with app.test_request_context('/generate-qr-code', method='POST'):
    assert request.path == '/generate-qr-code'
    assert request.method == 'POST'
