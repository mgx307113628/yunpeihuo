import unittest
import yphapp

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        print('setUp...')
        yphapp.app.config['TESTING'] = True
        self.app = yphapp.app.test_client()

    def tearDown(self):
        print('tearDown...')

    def test_index(self):
        print('test_index')
        rv = self.app.get('/')
        print(rv.data)
        #assert 'Hello World!' in rv.data
