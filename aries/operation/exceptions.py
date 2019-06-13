import json


class ClientError(Exception):

    def init(self, code):
        super(ClientError, self).__init__(code)
        self.code = code

    def send_to(self, channel):
        channel.send({
            'text': json.dumps({
                'error': self.code
            })
        })
