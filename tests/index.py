import os
import sys
import unittest

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

if __name__ == '__main__':
    d = os.path.abspath(__file__)
    workdir = os.path.dirname(os.path.dirname(d))
    sys.path.insert(0, workdir)
    print(sys.path)
    import yphapp

    unittest.main()
