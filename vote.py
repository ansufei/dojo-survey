from flask import Flask
from flask import render_template
from flask import request
import uuid
import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

memory = {}

def clean_outdated_surveys():
    to_remove = []
    if memory:
        for survey in memory.keys():
            if memory[survey].get('createdDate') < datetime.datetime.now(tz=pytz.timezone("Europe/Paris")) - datetime.timedelta(minutes=10):
                to_remove.append(survey)
    for k in to_remove:
        memory.pop(survey,None)
    return memory

sched = BackgroundScheduler(daemon=True)
sched.add_job(clean_outdated_surveys,'interval',seconds=10)
sched.start()

@app.get("/")
@app.get("/vote")
@app.get("/result")
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
def not_found(error):
    # manages 404 errors
    return render_template('error.html'), 404


@app.post('/generate-qr-code')
def number_of_options():
    # collects number of voting options and creates the survey object, with keys for numberOptions and created_date
    if request.json.get('numberOptions'):
        numberOptions = request.json.get('numberOptions')  
        survey_id = uuid.uuid4().hex
        memory[survey_id] = {}
        memory.get(survey_id)['createdDate'] = datetime.datetime.now(tz=pytz.timezone("Europe/Paris"))
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
                memory[survey_id]['numberVotes'] += 1
                return '<h1>Thank you!</h1>'
            return '<h1>Missing vote data</h1>'
        return '<h1>Wrong surveyId or survey expired</h1>'
    return '<h1>Missing surveyId</h1>'
        
@app.get('/result')
def return_votes():
    #returns json object {numberVotes:int,votes:int}
    if request.args.get('surveyId'):
        survey_id = request.args.get('surveyId')
        if memory.get(survey_id):
            number_votes = memory[survey_id]['numberVotes']
            result = memory[survey_id]['votes']
            return {"numberVotes": number_votes, "votes": result}
        return '<h1>Wrong surveyId or survey expired</h1>'
    
if __name__ == "__main__":
    app.run()

    
with app.test_request_context('/generate-qr-code', method='POST'):
    assert request.path == '/generate-qr-code'
    assert request.method == 'POST'
