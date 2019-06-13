from django.conf import settings
from rest_framework.parsers import BaseParser


class TextXmlParser(BaseParser):
    """
    text/xml parser
    """
    media_type = 'text/xml'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Simply return a string representing the body of the request.
        :param stream:
        :param media_type:
        :param parser_context:
        :return: string content
        """
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)
        data = stream.read().decode(encoding)

        return data
