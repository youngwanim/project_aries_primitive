
class Result(object):
    def __init__(self, code: object, message: object, response: object = None):
        self.code = code
        self.message = message
        self.response = response

    def get_code(self):
        return self.code

    def get_message(self):
        return self.message


class ResultResponse(object):
    def __init__(self, code: object, message: object, error_code=None):
        self.response = dict()
        self.response['code'] = code
        self.response['message'] = message
        if error_code is not None:
            self.response['error_code'] = error_code

    @classmethod
    def error_response(cls, code: object, message: object, error_code):
        response = ResultResponse(code, message)
        response.set_error(error_code)
        return response

    def set_code_message(self, code, message):
        self.response['code'] = code
        self.response['message'] = message

    def set(self, key, value):
        self.response[key] = value

    def set_map(self, data_set):
        if data_set is not None:
            self.response.update(data_set)

    def set_error(self, code):
        if code is not None:
            self.response['error_code'] = code

    def set_error_message(self, error_message):
        self.response['error_message'] = error_message

    def add(self, value):
        code = self.get_code()
        message = self.get_message()
        self.response = value
        self.response['code'] = code
        self.response['message'] = message

    def get_code(self):
        return self.response['code']

    def get_message(self):
        return self.response['message']

    def get_response(self):
        return self.response
