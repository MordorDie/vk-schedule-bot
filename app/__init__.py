from flask import Flask, request, json
from app import messageHandler
import os

app = Flask(__name__)

app.config.from_pyfile(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.cfg'), silent=True)


@app.route('/', methods=['POST'])
def processing():
    data = json.loads(request.data)
    if 'type' not in data.keys():
        return 'not vk'
    if data['type'] == 'confirmation':
        return app.config['CONFIRMATION_TOKEN']
    elif data['type'] == 'message_new':
        messageHandler.create_answer(data['object'], app.config['TOKEN'])
        return 'ok'
