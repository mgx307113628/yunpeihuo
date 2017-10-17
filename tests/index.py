import unittest
import yphapp

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        print('setUp...')
        app = yphapp.create_app('testing')
        self.clt = app.test_client()

    def tearDown(self):
        print('tearDown...')

    def test_index(self):
        print('test_index')
        rv = self.clt.get('/')
        print(rv.data)
        #assert 'Hello World!' in rv.data
