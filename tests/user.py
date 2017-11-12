import unittest
from flask import json
import yphapp


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        print('setUp...................................@')
        app = yphapp.create_app('testing')
        self.clt = app.test_client()#use_cookies=False

    def tearDown(self):
        print('tearDown................................@')

    def test_regitster(self):
        print('test_register ######')
        data = json.dumps({'account':'account001', 'password':'password001'})
        rsp = self.clt.post('/user/register', data=data)
        data = json.dumps({'account':'account002', 'password':'password002'})
        rsp = self.clt.post('/user/register', data=data)
        data = json.dumps({'account':'account003', 'password':'password003'})
        rsp = self.clt.post('/user/register', data=data)
        data = json.dumps({'account':'account004', 'password':'password004'})
        rsp = self.clt.post('/user/register', data=data)
        data = json.dumps({'account':'account005', 'password':'password005'})
        rsp = self.clt.post('/user/register', data=data)
        data = json.dumps({'account':'account006', 'password':'password006'})
        rsp = self.clt.post('/user/register', data=data)
        data = json.dumps({'account':'account007', 'password':'password007'})
        rsp = self.clt.post('/user/register', data=data)
        data = json.dumps({'account':'account008', 'password':'password008'})
        rsp = self.clt.post('/user/register', data=data)
        data = json.dumps({'account':'account009', 'password':'password009'})
        rsp = self.clt.post('/user/register', data=data)
        data = json.dumps({'account':'account010', 'password':'password010'})
        rsp = self.clt.post('/user/register', data=data)
        print('respond status:', rsp.status) 
        print('respond header:', rsp.headers)
        print('respond data:', str(rsp.data, encoding='utf-8'))
        #assert 'Hello World!' in rv.data

    #def test_login(self):
    #    print('test_login ######')
    #    data = json.dumps({'account':'account003', 'password':'password003'})
    #    rsp = self.clt.post('/user/login', data=data)
    #    print('respond status:', rsp.status) 
    #    print('respond header:', rsp.headers)
    #    print('respond data:', str(rsp.data, encoding='utf-8'))
    #    #assert 'Hello World!' in rv.data
