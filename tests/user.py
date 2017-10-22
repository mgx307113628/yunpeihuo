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

    def test_regitster(self):
        data = json.dumps({'account':'acc_qqqqqq', 'password':'pwd_000000'})
        rsp = self.clt.get('/user/register', data=data)
        print('respond:', str(rsp.data, encoding='utf-8'))
        #assert 'Hello World!' in rv.data

    #def test_query(self):
    #    import yphapp.models.mdaccount
    #    account = yphapp.models.mdaccount.Account.query.filter_by(acc='acc_aaabbb').one()
    #    print(account)
    #    print(account.transporter)
    #    print(account.consignor)

    #def test_query(self):
    #    return
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
