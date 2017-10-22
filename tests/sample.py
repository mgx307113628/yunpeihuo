import unittest
from flask import json
import yphapp


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        print('setUp...')
        app = yphapp.create_app('testing')
        self.clt = app.test_client()

    def tearDown(self):
        print('tearDown...')

    def test_index(self):
        s = json.dumps({'aaa':'yqibuqj'})
        print('test_index', s)
        rsp = self.clt.get('/', data=s)
        print('respond:', str(rsp.data, encoding='utf-8'))
        #assert 'Hello World!' in rv.data
