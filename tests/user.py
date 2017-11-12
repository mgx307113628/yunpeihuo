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

    #def test_regitster(self):
    #    data = json.dumps({'account':'account002', 'password':'password002'})
    #    rsp = self.clt.post('/user/register', data=data)
    #    print('respond:', str(rsp.data, encoding='utf-8'))
    #    #assert 'Hello World!' in rv.data

    #def test_query(self):
    #    import yphapp.models.md_account
    #    account = yphapp.models.md_account.Account.query.filter_by(acc='acc_aaabbb').one()
    #    print(account)
    #    print(account.transporter)
    #    print(account.consignor)

    def test_query(self):
        print('test_query1')
        data = json.dumps({"account":"account001"})
        rsp = self.clt.post('/user/query', data=data)
        print('respond status:', rsp.status) 
        print('respond header:', rsp.headers)
        print('respond data:', str(rsp.data, encoding='utf-8'))

    def test_query2(self):
        print('test_query2>>>>>>>>>>>>@')
        data = json.dumps({"account":"account002"})
        rsp = self.clt.post('/user/query', data=data)
        print('respond status:', rsp.status) 
        print('respond header:', rsp.headers)
        print('respond data:', str(rsp.data, encoding='utf-8'))

    #def test_query2(self):
    #    rsp = self.clt.get('/user/query')
    #    print('respond status:', rsp.status) 
    #    print('respond header:', rsp.headers)
    #    print('respond data:', str(rsp.data, encoding='utf-8'))

    #def test_login(self):
    #    return
    #    data = json.dumps({'account':'acc_aaabbb', 'password':'pwd_111222'})
    #    rsp = self.clt.get('/user/login', data=data)
    #    print('respond status:', rsp.status)
    #    print('respond header:', rsp.headers)
    #    print('respond data:', str(rsp.data, encoding='utf-8'))
