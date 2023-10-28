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
@app.get("/:surveyId")
def render_index():
    # returns index; or if surveyId is passed in the url, returns the number of options (saved in memory when the survey was created)
    if request.args.get('surveyId'):
        survey_id = request.args.get('surveyId')
        if memory.get(survey_id):
            return {"numberOptions": memory[survey_id]['numberOptions']}
        return '<h1>Wrong surveyId</h1>'
    return render_template('index.html')


@app.errorhandler(404)
def not_found():
    # manages 404 errors
    return render_template('error.html'), 404


@app.post('/generate-qr-code')
def number_of_options():
    # collects number of voting options and creates the survey object, with keys for numberOptions and created_date
    if request.json.get('numberOptions'):
        numberOptions = request.json.get('numberOptions')  
        survey_id = uuid.uuid4().hex
        memory[survey_id] = {}
        memory.get(survey_id)['createdDate'] = datetime.datetime.now()
        memory.get(survey_id)['numberOptions'] = numberOptions 
        memory.get(survey_id)['votes'] = {}
        memory.get(survey_id)['numberVotes'] = 0  
        return survey_id
    return '<h1>Number of options not given</h1>'

@app.post('/vote')
def collect_votes():
    # collects json object {surveyId:int, votes:int}
    if request.json.get('surveyId'):
        survey_id = request.json.get('surveyId')
        if memory.get(survey_id):
            if request.json.get('vote'):
                indiv_votes = request.json.get('vote')
                for index, value in indiv_votes.items():
                    if memory[survey_id]['votes'].get(index):
                        memory[survey_id]['votes'][index] += value
                    else:
                        memory[survey_id]['votes'][index] = value
                return '<h1>Thank you!</h1>'
            return '<h1>Missing vote data</h1>'
        return '<h1>Wrong surveyId</h1>'
    return '<h1>Missing surveyId</h1>'
        
@app.get('/result')
def return_votes():
    #returns json object {numberVotes:int,votes:int}
    pass

    
with app.test_request_context('/generate-qr-code', method='POST'):
    assert request.path == '/generate-qr-code'
    assert request.method == 'POST'
