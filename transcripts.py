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
    transcript_arg = request.args.get('call_number') + '.txt'

    transcript = transcript_arg.replace('.', '_')

    if api_key is None:
        return json.dumps(['Access denied.'])
    elif api_key != os.getenv('API_KEY'):
        return json.dumps(['Access denied.'])

    transcript_text = ''
    with open(transcripts_path + '/' + transcript, 'r') as var:
        for line in var:
            line = line.replace('\n', ' ')
            transcript_text += line

    return json.dumps(dict(transcript=transcript_text))


serve(app, host='0.0.0.0', port=8081)
