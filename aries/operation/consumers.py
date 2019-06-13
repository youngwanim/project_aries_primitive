import json

import logging
import requests
from channels import Group

from aries.common import code
from aries.common import urlmapper
from aries.operation.models import HubRequest, HubResponse


def on_connect(message):
    message.reply_channel.send({'accept': True})
    Group('operation').add(message.reply_channel)
    print(message.reply_channel)


def on_disconnect(message):
    message.reply_channel.send({'close': True})
    Group('operation').discard(message.reply_channel)


def message_handler(message):
    print(message.reply_channel)
    message_text = message.content['text']
    print('Receive message : ' + message_text)

    host = urlmapper.get_url('OPERATION_API')

    try:
        hub_request = parse_request_message(message_text)
        headers = {'Authorization': 'bearer ' + hub_request.access_token}

        if hub_request.method == 'get':
            response = requests.get(host + hub_request.api_path, headers=headers)
        elif hub_request.method == 'post':
            json_data = json.loads(hub_request.payload)
            response = requests.post(host + hub_request.api_path, headers=headers, json=json_data)
        elif hub_request.method == 'put':
            json_data = json.loads(hub_request.payload)
            response = requests.put(host + hub_request.api_path, headers=headers, json=json_data)
        else:
            response = requests.delete(host + hub_request.api_path, headers=headers)

        response_json = response.json()
        hub_response = HubResponse('response', hub_request.domain)
        hub_response.code = response_json['code']
        hub_response.message = response_json['message']

        if response.status_code == code.ARIES_200_SUCCESS:
            hub_response.result = response_json['result']
        elif response.status_code == code.ARIES_500_INTERNAL_SERVER_ERROR:
            hub_response.set_error_code(response_json['error_code'])
            hub_response.result = ''

        response_data = {
            'text': json.dumps(hub_response.get_json_object())
        }

        message.reply_channel.send(response_data)
    except Exception as e:
        print(e)


def keep_alive_message(message):
    logger = logging.getLogger(__name__)
    logger.info('websocket_keepalive. message = %s', message)
    Group('operation').add(message.reply_channel)


def parse_request_message(message):
    message_json = json.loads(message)
    return HubRequest(message_json)
