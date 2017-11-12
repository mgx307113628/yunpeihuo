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

    def gen_dpt_lct(self):
        return {
                   'region' : ['广东省', '深圳市', '宝安区', '西乡街道', '某某物流园'],
                   'detail' : '某某大楼',
                   'coords' : [1111.11, 2222.22],
               }

    def gen_dst_lct(self):
        return {
                   'region' : ['广东省', '广州市', '越秀区', '', 'XYZ物流园'],
                   'detail' : 'ABC大楼',
                   'coords' : [3333.33, 4444.44],
               }


    def gen_cargo(self):
        return [{
                    'name' : '红酒',
                    'type' : '红酒',
                    'number' : 100,
                    'weight' : 333,
                    'volumn' : 444,
                },
                {
                    'name' : 'iphone',
                    'type' : 'iphone',
                    'number' : 700,
                    'weight' : 761,
                    'volumn' : 987,
                },]


    #def test_addneworder(self):
    #    print('test_addneworder')
    #    od = {}
    #    od['cargo_type'] = 1# <int>货物类型(1:标准货物 2:非标准货物),
    #    od['rent_type'] = 1# <int>用车类型(1:按重量体积 2:包车),
    #    od['times'] = [1509465600, 3600, 1509811200, 3600] # [<int>出发时间戳, <int>装货时间(单位:秒), <int>达到时间戳, <int>御货时间(单位:秒)],
    #    od['loader'] = ['张三', '13077778888'] # [<string>装货者姓名, <string>装货者手机],
    #    od['unloader'] = ['李四', '15966669999'] # [<string>卸货者姓名, <string>卸货者手机],
    #    od['cargo'] = self.gen_cargo() # [<json>货物,...],
    #    od['lct_depart'] = self.gen_dpt_lct() # <json>出发地址,
    #    od['lct_dest'] = self.gen_dst_lct() # <json>目的地址,

    #    data = {'accid':1, 'order':od}

    #    #od['orderid' : <string>订单号,
    #    #od['status' : <int>订单状态,
    #    #od['cargo_type' : <int>货物类型(1:标准货物 2:非标准货物),
    #    #od['rent_type' : <int>用车类型(1:按重量体积 2:包车),
    #    #od['lct_depart' : <json>出发地址,
    #    #od['lct_dest' : <json>目的地址,
    #    #od['times' : [<int>出发时间戳, <int>装货时间(单位:秒), <int>达到时间戳, <int>御货时间(单位:秒)],
    #    #od['loader' : [<string>装货者姓名, <string>装货者手机],
    #    #od['unloader' : [<string>卸货者姓名, <string>卸货者手机],
    #    #od['cargo' : [<json>货物,...],

    #    rsp = self.clt.post('/order/new', data=json.dumps(data))
    #    rsp = self.clt.post('/order/new', data=json.dumps(data))
    #    rsp = self.clt.post('/order/new', data=json.dumps(data))
    #    rsp = self.clt.post('/order/new', data=json.dumps(data))
    #    print('respond status:', rsp.status) 
    #    print('respond header:', rsp.headers)
    #    print('respond data:', str(rsp.data, encoding='utf-8'))

    def test_queryorder(self):
        rsp = self.clt.post('/order/list', data=json.dumps({'current':0,'num':10}))
        print('respond status:', rsp.status) 
        print('respond header:', rsp.headers)
        print('respond data:', str(rsp.data, encoding='utf-8'))
        ob = json.loads(str(rsp.data, encoding='utf-8'))
        dt = ob['data']['orders']
        print("length:%d"%len(dt))
        for x in dt:
            print('orderid:%s'%x['orderid'])
