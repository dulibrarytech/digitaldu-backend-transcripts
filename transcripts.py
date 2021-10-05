import json
import os
from os.path import join, dirname

from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from waitress import serve

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

transcripts_path = os.getenv('TRANSCRIPTS_PATH')

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

'''
Renders Transcripts API Information
@returns: String
'''


@app.route('/', methods=['GET'])
def index():
    return 'DigitalDU-Transcripts v0.1.0'


'''
Get transcript by call number
@param: api_key
@returns: Json
'''


@app.route('/api/v1/transcript', methods=['GET'])
def get_transcript():
    api_key = request.args.get('api_key')
    transcript_arg = request.args.get('call_number')

    if api_key is None:
        return json.dumps(dict(error='true', message='Access denied.')), 401
    elif api_key != os.getenv('API_KEY'):
        return json.dumps(dict(error='true', message='Access denied.')), 401

    if transcript_arg is None:
        return json.dumps(dict(error='true', message='Resource not found.')), 404

    # get transcript file names and ignore hidden files
    transcripts = [f for f in os.listdir(transcripts_path + '/' + transcript_arg) if not f.startswith('.')]

    for i in transcripts:

        # copy transcript data into new file
        try:
            with open(transcripts_path + transcript_arg + '/' + transcript_arg + '.txt', 'a') as outfile:
                for transcript_file in transcripts:
                    with open(transcripts_path + transcript_arg + '/' + transcript_file) as file:
                        outfile.write(file.read())
        except:
            return json.dumps(dict(error='true', message='Unable to concatenate transcript data.')), 500

    # remove new line characters from transcript data
    try:
        transcript_text = ''
        with open(transcripts_path + transcript_arg + '/' + transcript_arg + '.txt', 'r') as transcript:
            for line in transcript:
                line = line.replace('\n', ' ')
                transcript_text += line

    except:
        return json.dumps(dict(error='true', message='Unable to read transcript data.')), 500

    # delete transcript import file if it exists
    if (os.path.isfile(transcripts_path + transcript_arg + '/' + transcript_arg + '.txt')):
        os.remove(transcripts_path + transcript_arg + '/' + transcript_arg + '.txt')

    return json.dumps(dict(transcript=transcript_text, error='false', message='Resource found.')), 200

serve(app, host='0.0.0.0', port=8081)
