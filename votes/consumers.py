# chat/consumers.py
from channels.generic.websocket import WebsocketConsumer
import json
from .models import Community, Survey, Question, Response, ResponseVote

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    # Received request to update vote information
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        survey_id = text_data_json['survey_id']

        response_percents = Survey.get_response_percents(survey_id)
        self.send(text_data=json.dumps({
            'message': "20",
            'username': username,
            'response_percents': response_percents
        }))
