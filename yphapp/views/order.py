import threading
from flask import Blueprint, request, jsonify, json
from .. import app, db, data
from ..models.indent import Indent, IndentNum, IndentStatus
from werkzeug.local import Local
from ..define import *
import time
import random
import datetime

bp_order = Blueprint('order', __name__) 

order_id_pool = Local()
step_size = 10000


def gen_order_id():
    """
    :return: 订单号
    订单号格式(共11位):
    1位业务类型 + 1位进程ID + 1位线程ID + 2位degree + 4位序列数字 + 2位随机数字
    degree+序列数字 取值为0到999999,共一百万个

    由于订单号格式,有以下限制:
    1. 必须使用uwsgi开启应用
    2. work进程数量不得超过10个
    3. 每个work进程的线程数量不得超过10个
    4. 订单号最多数量为1000000个, 可通过增加degree位数增加订单号数量

    订单号存于indent表,为MYSQL的BIGINT类型,一定要注意不要溢出
    BIGINT无符号数范围：0 ~ 18446744073709551615
    BIGINT有符号数范围：-9223372036854775808 ~ 9223372036854775807
    """
    tname = threading.current_thread().name
    if type(tname) is bytes:
        tname = str(tname, encoding='utf8')
    #用uwsgi启动,每个进程最多线程数为10个: uWSGIWorker1Core0
    if tname[:13] == "b'uWSGIWorker" and tname[14:18] == 'Core':
        process = int(tname[13])
        thread = int(tname[18])
        if process >= 10 or thread >= 10:
            raise RuntimeError()
    #用python启动单进程(用于开发和测试)
    elif tname == 'MainThread':
        process = 0
        thread = 0
    elif tname[:7] == 'Thread-':
        process = 0
        thread = int(tname[7])
    else:
        raise RuntimeError()

    refresh = False
    indent_num = IndentNum.query.filter_by(process=process, thread=thread).first()
    if indent_num is None:
        degree = index = 0
        indent_num = IndentNum(process, thread, degree, index)
        db.session.add(indent_num)
        refresh = True
    else:
        indent_num.index += 1
        if indent_num.index >= step_size:
            indent_num.degree += 1
            indent_num.index = 0
            refresh = True
        degree = indent_num.degree
        index = indent_num.index
    db.session.commit()

    sequence = getattr(order_id_pool, 'sequence', None)
    if sequence is None or refresh:
        sequence = []
        lst = list(range(step_size))
        crtidx = len(lst)-1
        random.seed(71634+degree) #保证每一阶段,服务器重启后生成的号码序列都一样
        while crtidx >= 0:
            i = random.randint(0, crtidx)
            sequence.append(lst[i])
            lst[i], lst[crtidx]= lst[crtidx], lst[i]
            crtidx -= 1
        random.seed(int(time.time()))
    setattr(order_id_pool, 'sequence', None)
    num = sequence[index]

    rd = random.randint(0, 99)

    return int('1%d%d%.2d%.4d%.2d'%(process, thread, degree, num, rd)) #共11位

#{
#    'region' : ['广东省', '深圳市', '宝安区', '西乡街道', '某某物流园'],
#    'detail' : "某某街某某号",
#    'coords' : [400.3111, 666.77777],
#

class Order:
    ORDER_PROP = [
        'orderid',
        'csgid',
        'tspid',
        'cargo_type',
        'rent_type',
        'price',
        'status',
        'dpt_lctcode',
        'dpt_lctdtl',
        'dpt_lctlong',
        'dpt_lctlat',
        'dpt_tmclk',
        'dpt_tmload',
        'dpt_ldrname',
        'dpt_ldrphone',
        'dst_lctcode',
        'dst_lctdtl',
        'dst_lctlong',
        'dst_lctlat',
        'dst_tmclk',
        'dst_tmunload',
        'dst_uldrname',
        'dst_uldrphone',
        'cargo',
        'weight',
        'volume',
    ]
    def __init__(self, **kwargs):
        self.orderid = None
        self.csgid = None
        self.tspid = None
        self.cargo_type = None
        self.rent_type = None
        self.price = None
        self.status = None
        self.dpt_lctcode = None
        self.dpt_lctdtl = None
        self.dpt_lctlong = None
        self.dpt_lctlat = None
        self.dpt_tmclk = None
        self.dpt_tmload = None
        self.dpt_ldrname = None
        self.dpt_ldrphone = None
        self.dst_lctcode = None
        self.dst_lctdtl = None
        self.dst_lctlong = None
        self.dst_lctlat = None
        self.dst_tmclk = None
        self.dst_tmunload = None
        self.dst_uldrname = None
        self.dst_uldrphone = None
        self.cargo = None
        self.weight = None
        self.volume = None

        for k, v in kwargs.items():
            setattr(self, k, v)
        self.update = True
        self.cache = None

    def CalculatePrice(self):
        self.price = random.randint(1000, 9000)
        #TODO 似乎没有随机性
        self.update = True

    def InsertTable(self):
        indentob = Indent(self.orderid, **self.__dict__)
        db.session.add(indentob)
        db.session.commit()

    def encode_order_data(self):
        if not self.update and self.cache is not None:
            return self.cache
        data = {}
        data['orderid'] = str(self.orderid)
        data['status'] = self.status
        data['cargo_type'] = self.cargo_type
        data['rent_type'] = self.rent_type
        data['price'] = self.price
        data['lct_depart'] = encode_locate(self.dpt_lctcode, self.dpt_lctdtl, self.dpt_lctlong, self.dpt_lctlat,)
        data['lct_dest'] = encode_locate(self.dst_lctcode, self.dst_lctdtl, self.dst_lctlong, self.dst_lctlat,)
        data['times'] = [self.dpt_tmclk, self.dpt_tmload, self.dst_tmclk, self.dst_tmunload,]
        data['loader'] = [self.dpt_ldrname, self.dpt_ldrphone,]
        data['unloader'] = [self.dst_uldrname, self.dst_uldrphone,]
        data['cargo'] = self.cargo
        self.cache = data
        return self.cache

    def Take(self, accid):
        indentob = Indent.query.filter_by(id=self.orderid).one()
        indentob.tspid = accid
        indentob.status.status = INDENT_STATUS_GOTOSTART
        db.session.commit()
        self.tspid = accid
        self.status = INDENT_STATUS_GOTOSTART
        self.update = True

    def SetStatus(self, status):
        indentob = Indent.query.filter_by(id=self.orderid).one()
        indentob.status.status = status
        db.session.commit()
        self.status = status
        self.update = True


class OrderPool:
    _instance = None
    _initflag = False
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if OrderPool._initflag == False:
            OrderPool._initflag = True
            self.order_dct = {}
            self.order_lst = []
            self.csg_orders = {}
            self.tsp_orders = {}
            self.update = False

    def init_pool(self):
        for indentob in Indent.query.all():
            order = Order()
            indentob.SyncProp(order.__dict__)
            self.order_dct[order.orderid] = order
            self.order_lst.append(order)
            self.csg_orders.setdefault(order.csgid, []).append(order)
            if order.tspid:
                self.tsp_orders.setdefault(order.tspid, []).append(order)
        self.update = True
        return

    def add_new_order(self, accid, orderid, orderdata):
        orderdata.update({'orderid':orderid,
                            'csgid':accid,
                            'status':INDENT_STATUS_PUBLISHING,
                            'crttime':datetime.datetime.now()})
        order = Order(**orderdata)
        order.CalculatePrice()
        order.InsertTable()
        self.order_dct[orderid] = order
        self.order_lst.append(order)
        self.csg_orders.setdefault(accid, []).append(order)
        self.update = True

    def show_orders(self, current, num):
        return self._send_list(self.order_lst, current, num)

    def _send_list(self, orderlst, current, num):
        send_data = []
        send_flag = False
        n = 0
        if current == 0:
            send_flag = True
        for idx, order in enumerate(orderlst):
            if send_flag == True:
                send_data.append(order.encode_order_data())
                n += 1
                if n >= num:
                    break
            elif idx+1 == current:
                send_flag = True
        return jsonify(code=0, msg='success', data={'orders':send_data})

    def take_order(self, accid, orderid):
        order = self.order_dct.get(orderid)
        if order is None:
            return jsonify(code=1, msg='order not exist')
        order.Take(accid)
        self.tsp_orders.setdefault(accid, []).append(order)
        self.update = True
        return jsonify(code=0, msg='success', data={'orderid':str(orderid)})

    def list_mine(self, accid, role, current, num):
        if role == ROLE_TYPE_CSGN:
            orderlst = self.csg_orders.get(accid, [])
        elif role == ROLE_TYPE_TRSP:
            orderlst = self.tsp_orders.get(accid, [])
        else:
            raise RuntimeError
        return self._send_list(orderlst, current, num)

    def list_comp(self, accid, role, current, num):
        if role == ROLE_TYPE_CSGN:
            idtlst = Indent.query.join(IndentStatus).filter(Indent.csgid==accid, IndentStatus.status==INDENT_STATUS_COMPLETE).order_by(Indent.id)[current:current+num]
        elif role == ROLE_TYPE_TRSP:
            idtlst = Indent.query.join(IndentStatus).filter(Indent.tspid==accid, IndentStatus.status==INDENT_STATUS_COMPLETE).order_by(db.desc(Indent.id))[current:current+num]
        else:
            raise RuntimeError
        orderlst = []
        for idt in idtlst:
            order = Order()
            idt.SyncProp(order.__dict__)
            orderlst.append(order)
        return self._send_list(orderlst, 0, len(orderlst))

    def event_order(self, accid, orderid, event):
        event_status = {
                'start':3,
                'load_complete':4,
                'load_confirm':5,
                'arrive':6,
                'unload_complete':7,
                'unload_confirm':8,
        }
        order = self.order_dct.get(orderid)
        order.SetStatus(event_status[event])
        return jsonify(code=0, msg='success', data={'orderid':str(orderid)})

def encode_locate(code, detail, longitude, latitude):
    dct = {}
    dct['region'] = data.CODE_LOCATION.get(code)
    dct['detail'] = detail
    dct['coords'] = [longitude, latitude]
    return dct
    
def decode_locate(location):
    region = location.get('region')
    if region is None:
        raise RuntimeError()
    code = data.LOCATION_CODE.get(tuple(region))
    if code is None:
        raise RuntimeError()
    detail = location.get('detail')
    longitude, latitude = location.get('coords')
    return code, detail, longitude, latitude

def decode_order_data(data):
    od = {}

    status = data.get('status')
    cargo_type = data.get('cargo_type')
    rent_type = data.get('rent_type')
    lct_depart = data.get('lct_depart')
    lct_dest = data.get('lct_dest')
    tmlst = data.get('times')
    loader = data.get('loader')
    unloader = data.get('unloader')
    cargo = data.get('cargo')

    od['status'] = status

    if (cargo_type is None or rent_type is None or lct_depart is None
        or lct_dest is None or tmlst is None or loader is None
        or unloader is None):
        raise RuntimeError()

    if cargo_type not in CARGO_TYPE_ALL:
        raise RuntimeError()
    od['cargo_type'] = cargo_type

    if rent_type not in RENT_TYPE_ALL:
        raise RuntimeError()
    od['rent_type'] = rent_type

    code, detail, lon, lat = decode_locate(lct_depart)
    od['dpt_lctcode'] = code
    od['dpt_lctdtl'] = detail
    od['dpt_lctlong'] = lon
    od['dpt_lctlat'] = lat

    code, detail, lon, lat = decode_locate(lct_dest)
    od['dst_lctcode'] = code
    od['dst_lctdtl'] = detail
    od['dst_lctlong'] = lon
    od['dst_lctlat'] = lat

    #if not (tmlst[0] <= tmlst[1] < tmlst[2] <= tmlst[3]):
    #    raise RuntimeError()
    od['dpt_tmclk'] = tmlst[0]
    od['dpt_tmload'] = tmlst[1]
    od['dst_tmclk'] = tmlst[2]
    od['dst_tmunload'] = tmlst[3]

    od['dpt_ldrname'] = loader[0]
    od['dpt_ldrphone'] = loader[1]
    od['dst_uldrname'] = unloader[0]
    od['dst_uldrphone'] = unloader[1]

    od['cargo'] = cargo

    return od

@bp_order.route('/new', methods=['POST'])
def order_new():
    print("order_new 000")
    dt = request.get_json(True)
    accid = dt.get('accid')
    orderdata = decode_order_data(dt.get('order'))
    print("order_new 111 %s"%(accid))
    orderid = gen_order_id()
    new_order = OrderPool().add_new_order(accid, orderid, orderdata)
    return jsonify(code=0, msg='success', data={'orderid':str(orderid)})

@bp_order.route('/list', methods=['POST'])
def order_list():
    print('order_list 111111111111111')
    dt = request.get_json(True)
    current = int(dt.get('current', 0))
    num = int(dt.get('num'))
    print('order_list 222222222222222', current, num)
    return OrderPool().show_orders(current, num)

@bp_order.route('/take', methods=['POST'])
def order_take():
    print('order_take 111111111111111')
    dt = request.get_json(True)
    accid = int(dt.get('accid'))
    orderid = int(dt.get('orderid'))
    print('order_take 222222222222222 acc:%d  orderid:%d'%(accid, orderid))
    return OrderPool().take_order(accid, orderid)

@bp_order.route('/cancel', methods=['POST'])
def order_cancel():
    print('order_cancel 111111111111111')
    dt = request.get_json(True)
    accid = int(dt.get('accid'))
    orderid = int(dt.get('orderid'))
    print('order_cancel 222222222222222 acc:%d  orderid:%d'%(accid, orderid))
    raise RuntimeError

@bp_order.route('/list_mine', methods=['POST'])
def order_list_mine():
    print('order_list_mine 111111111111111')
    dt = request.get_json(True)
    accid = int(dt.get('accid'))
    role = int(dt.get('role'))
    current = int(dt.get('current', 0))
    num = int(dt.get('num'))
    print('order_list_mine 222222222222222 acc:%d role:%d current:%d num:%d'%(accid, role, current, num))
    return OrderPool().list_mine(accid, role, current, num)

@bp_order.route('/list_comp', methods=['POST'])
def order_list_comp():
    print('order_list_comp 111111111111111')
    dt = request.get_json(True)
    accid = int(dt.get('accid'))
    role = int(dt.get('role'))
    current = int(dt.get('current', 0))
    num = int(dt.get('num'))
    print('order_list_comp 222222222222222 acc:%d role:%d current:%d num:%d'%(accid, role, current, num))
    return OrderPool().list_comp(accid, role, current, num)

@bp_order.route('/setphoto', methods=['POST'])
def order_setphoto():
    raise RuntimeError
    print('order_setphoto 111111111111111')
    dt = request.get_json(True)
    accid = int(dt.get('accid'))
    role = int(dt.get('role'))
    current = int(dt.get('current', 0))
    num = int(dt.get('num'))
    print('order_setphoto 222222222222222 acc:%d role:%d current:%d num:%d'%(accid, role, current, num))
    return OrderPool().setphoto(accid, role, current, num)

@bp_order.route('/start', methods=['POST'])
def order_start():
    event = 'start'
    print('order_event: %s 111111111111111'%event)
    dt = request.get_json(True)
    accid = int(dt.get('accid'))
    orderid = int(dt.get('orderid'))
    print('order_event: %s 222222222222222 acc:%d  orderid:%d'%(event, accid, orderid))
    return OrderPool().event_order(accid, orderid, status)
@bp_order.route('/load_complete', methods=['POST'])
def order_load_comp():
    event = 'load_complete'
    print('order_event: %s 111111111111111'%event)
    dt = request.get_json(True)
    accid = int(dt.get('accid'))
    orderid = int(dt.get('orderid'))
    print('order_event: %s 222222222222222 acc:%d  orderid:%d'%(event, accid, orderid))
    return OrderPool().event_order(accid, orderid, status)
@bp_order.route('/load_confirm', methods=['POST'])
def order_load_confirm():
    event = 'load_confirm'
    print('order_event: %s 111111111111111'%event)
    dt = request.get_json(True)
    accid = int(dt.get('accid'))
    orderid = int(dt.get('orderid'))
    print('order_event: %s 222222222222222 acc:%d  orderid:%d'%(event, accid, orderid))
    return OrderPool().event_order(accid, orderid, status)
@bp_order.route('/arrive', methods=['POST'])
def order_arrive():
    event = 'arrive'
    print('order_event: %s 111111111111111'%event)
    dt = request.get_json(True)
    accid = int(dt.get('accid'))
    orderid = int(dt.get('orderid'))
    print('order_event: %s 222222222222222 acc:%d  orderid:%d'%(event, accid, orderid))
    return OrderPool().event_order(accid, orderid, status)
@bp_order.route('/unload_complete', methods=['POST'])
def order_unload_comp():
    event = 'unload_complete'
    print('order_event: %s 111111111111111'%event)
    dt = request.get_json(True)
    accid = int(dt.get('accid'))
    orderid = int(dt.get('orderid'))
    print('order_event: %s 222222222222222 acc:%d  orderid:%d'%(event, accid, orderid))
    return OrderPool().event_order(accid, orderid, status)
@bp_order.route('/unload_confirm', methods=['POST'])
def order_unload_confirm():
    event = 'unload_confirm'
    print('order_event: %s 111111111111111'%event)
    dt = request.get_json(True)
    accid = int(dt.get('accid'))
    orderid = int(dt.get('orderid'))
    print('order_event: %s 222222222222222 acc:%d  orderid:%d'%(event, accid, orderid))
    return OrderPool().event_order(accid, orderid, status)
