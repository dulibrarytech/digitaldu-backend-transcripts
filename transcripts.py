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


@app.route('/', methods=['GET'])
def index():
    """
    App Information
    :return: String
    """
    return 'DigitalDU-Transcripts v0.6.0'


@app.route('/api/v1/transcript', methods=['GET'])
def get_transcript():
    """
    Get transcript by call number
    :return: String
    """
    api_key = request.args.get('api_key').strip()
    transcript_arg = request.args.get('call_number').strip()

    if api_key is None:
        return json.dumps(dict(error='true', message='Access denied.')), 403
    elif api_key != os.getenv('API_KEY'):
        return json.dumps(dict(error='true', message='Access denied.')), 403

    if transcript_arg is None:
        return json.dumps(dict(error='true', message='Resource not found.')), 404

    transcript_ingest_path = f'{transcripts_path}/{transcript_arg}'

    transcripts = None
    try:
        transcripts = [f for f in os.listdir(transcript_ingest_path) if not f.startswith('.')]
        transcripts.sort()

    except:
        return json.dumps(dict(error='true', message='Resource not found.')), 404

    transcript_list = []
    transcript_search = ''

    for i in transcripts:

        # populate transcript_list and transcript_search
        try:
            with open(f'{transcript_ingest_path}/{i}', 'r') as transcript:
                transcript_text = transcript.read()
                transcript_list.append(dict(call_number=i.replace('.txt', ''), transcript_text=transcript_text))

                transcript_search += transcript_text.replace('\n', ' ')

        except:
            return json.dumps(dict(error='true', message='Unable to read or concatenate transcript data.')), 500

    return json.dumps(dict(transcripts=transcript_list, transcript_search=transcript_search, error='false', message='Resource found.')), 200


serve(app, host='0.0.0.0', port=8081)
