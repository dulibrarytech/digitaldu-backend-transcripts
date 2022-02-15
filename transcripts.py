import json
import os
from os.path import isfile, join, dirname

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

    try:
        transcripts = [f for f in os.listdir(transcript_ingest_path) if not f.startswith('.')]
    except:
        return json.dumps(dict(error='true', message='Resource not found.')), 404

    transcript_list = []
    transcript_search = ''

    for i in transcripts:

        try:
            with open(f'{transcript_ingest_path}/{i}', 'r') as transcript:
                transcript_text = transcript.read()
                transcript_list.append(dict(call_number=i.replace('.txt', ''), transcript_text=transcript_text))

        except:
            return json.dumps(dict(error='true', message='Unable to read transcript data.')), 500

    for i in transcripts:

        # copy transcript data into new file
        try:
            with open(f'{transcript_ingest_path}/{transcript_arg}.txt', 'a') as outfile:
                for transcript_file in transcripts:
                    with open(f'{transcript_ingest_path}/{transcript_file}', 'r') as file:
                        outfile.write(file.read())
        except:
            return json.dumps(dict(error='true', message='Unable to concatenate transcript data.')), 500

        # remove new line characters from transcript data
    try:
        with open(f'{transcript_ingest_path}/{transcript_arg}.txt', 'r') as transcript:
            transcript_search = transcript.read().replace('\n', ' ')

    except:
        return json.dumps(dict(error='true', message='Unable to read transcript data.')), 500

        # delete transcript import file if it exists
    if isfile(f'{transcript_ingest_path}/{transcript_arg}.txt'):
        os.remove(f'{transcript_ingest_path}/{transcript_arg}.txt')

    return json.dumps(dict(transcripts=transcript_list, transcript_search=transcript_search, error='false', message='Resource found.')), 200


serve(app, host='0.0.0.0', port=8081)
