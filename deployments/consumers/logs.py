import json
from time import sleep
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        sleep(1)
        self.send(text_data=json.dumps({
            'message': "Restarting App with PID"
        }))
        sleep(2)
        self.send(text_data=json.dumps({
            'message': "HTTP GET /socket.io/?EIO=4"
        }))
        sleep(1)
        self.send(text_data=json.dumps({
            'message': "Not Found: /socket.io/"
        }))
        sleep(2)
        self.send(text_data=json.dumps({
            'message': "HTTP POST /logs/"
        }))
        sleep(1)
        self.send(text_data=json.dumps({
            'message': "Not Found: /deployment/123112/dkw/user/"
        }))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))
