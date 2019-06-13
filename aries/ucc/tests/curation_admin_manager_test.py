import json
import logging

from django.test import TestCase


class TestCurationAdmin(TestCase):

    def setUp(self):
        logger_info = logging.getLogger('ucc_info')
        logger_error = logging.getLogger('ucc_error')

    def test_article_service(self):
        pass

    pass
