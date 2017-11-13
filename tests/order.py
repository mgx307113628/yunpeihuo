import unittest
from flask import json
import yphapp
import time


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        print('setUp...................................@')
        app = yphapp.create_app('testing')
        self.clt = app.test_client()#use_cookies=False

    def tearDown(self):
        print('tearDown................................@')

    def test_queryorder(self):
        return
        rsp = self.clt.post('/order/list', data=json.dumps({'current':0,'num':10}))
        print('respond status:', rsp.status) 
        print('respond header:', rsp.headers)
        print('respond data:', str(rsp.data, encoding='utf-8'))
        ob = json.loads(str(rsp.data, encoding='utf-8'))
        dt = ob['data']['orders']
        print("length:%d"%len(dt))
        for x in dt:
            print('orderid:%s'%x['orderid'])

    def gen_one_cargo(self, lst):
        return {
                   'name' : lst[0],
                   'type' : lst[1],
                   'number' : int(lst[2]),
                   'volumn' : int(lst[3]),
                   'weight' : int(lst[4]),
               }

    def gen_one_lct(self, *lst):
        return {
                   'region' : [lst[0], lst[1], lst[2], lst[3], lst[4]],
                   'detail' : lst[5],
                   'coords' : [lst[6], lst[7]],
               }


    def test_addneworder_fromdata(self):
        return
        cargos = {}
        f = open("/home/karas/cargo.txt")
        for line in f.readlines():
            lst = line.split()
            cargo_id = 0
            if len(lst) == 6:
                cargo_id = int(lst.pop(0))
                cg_lst = cargos.setdefault(cargo_id, [])
            cg_lst.append(self.gen_one_cargo(lst))
        f.close()
        f = open("/home/karas/order.txt")
        for line in f.readlines():
            lst = line.split()
            od = {}
            od['cargo_type'] = 1# <int>货物类型(1:标准货物 2:非标准货物),
            od['rent_type'] = 1# <int>用车类型(1:按重量体积 2:包车),
            t1 = int(time.mktime(time.strptime(lst[6], '%Y/%m/%d/%H:%M')))
            t2 = int(time.mktime(time.strptime(lst[18], '%Y/%m/%d/%H:%M')))
            od['times'] = [t1, int(lst[7]), t2, int(lst[19])] # [<int>出发时间戳, <int>装货时间(单位:秒), <int>达到时间戳, <int>御货时间(单位:秒)],
            od['loader'] = ['李先生', '13760474247'] # [<string>装货者姓名, <string>装货者手机],
            od['unloader'] = ['王先生', '13714082391'] # [<string>卸货者姓名, <string>卸货者手机],
            od['cargo'] = cargos[int(lst[28])] # [<json>货物,...],
            od['lct_depart'] = self.gen_one_lct(lst[8],lst[9],lst[10],lst[11],lst[12],lst[15],lst[4],lst[5])
            od['lct_dest'] = self.gen_one_lct(lst[20],lst[21],lst[22],lst[23],lst[24],lst[27],lst[16],lst[17])
            data = {'accid':1, 'order':od}
            rsp = self.clt.post('/order/new', data=json.dumps(data))
        f.close()
        print('respond status:', rsp.status) 
        print('respond header:', rsp.headers)
        print('respond data:', str(rsp.data, encoding='utf-8'))

    def test_querymine(self):
        rsp = self.clt.post('/order/list_mine', data=json.dumps({'accid':4,'role':1,'current':0,'num':10}))
        print('respond status:', rsp.status) 
        print('respond header:', rsp.headers)
        print('respond data:', str(rsp.data, encoding='utf-8'))
        ob = json.loads(str(rsp.data, encoding='utf-8'))
        dt = ob['data']['orders']
        print("length:%d"%len(dt))
        for x in dt:
            print('orderid:%s'%x['orderid'])

