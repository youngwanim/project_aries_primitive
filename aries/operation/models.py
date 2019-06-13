

class HubRequest(object):
    def __init__(self, request_data):
        self.request_id = request_data['request_id']
        self.timestamp = request_data['timestamp']
        self.domain = request_data['domain']
        self.api_path = request_data['api_path']
        self.method = request_data['method']
        self.payload = request_data['payload']
        self.access_token = request_data['access_token']


class HubResponse(object):

    def __init__(self, message_type, domain):
        self.type = message_type
        self.domain = domain
        self.code = 200
        self.error_code = 0
        self.message = 'success'
        self.result = ''

    def set_error_code(self, error_code):
        self.error_code = error_code

    def get_json_object(self):

        return {'type': self.type, 'domain': self.domain, 'code': self.code,
                'error_code': self.error_code, 'message': self.message, 'result': self.result}
