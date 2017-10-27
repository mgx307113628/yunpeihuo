import threading
from flask import Blueprint, request, jsonify, json
from .. import app, db, data
from ..models import md_indent
from werkzeug.local import Local
from ..define import *
import time
import random

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
    indent_num = md_indent.IndentNum.query.filter_by(process=process, thread=thread).first()
    if indent_num is None:
        degree = index = 0
        indent_num = md_indent.IndentNum(process, thread, degree, index)
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

class IndentPool():
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(IndentPool).__new__(cls, *args, **kwargs)
        return cls._instance

    def __int__(self):
        self.indents = {}
        self.update = False

    def init_pool(self):
        pass

    def add_new_order(self, accid, orderid, orderinfo):
        kwargs = {}
        self.parse_orderinfo(kwargs, orderinfo)
        indent = md_indent.Indent(orderid, accid, **kwargs)
        db.session.add(indent)
        db.session.commit()
        self.indents[orderid] = indent
        self.update = True

    def parse_orderinfo(self, kwargs, info):
        cargo_type = info.get('cargo_type')
        rent_type = info.get('rent_type')
        lct_depart = info.get('lct_depart')
        lct_dest = info.get('lct_dest')
        tmlst = info.get('timestamps')
        loader = info.get('loader')
        unloader = info.get('unloader')
        cargo = info.get('cargo')

        if (cargo_type is None or rent_type is None or lct_depart is None
            or lct_dest is None or tmlst is None or loader is None
            or unloader is None):
            raise RuntimeError()

        if cargo_type not in CARGO_TYPE_ALL:
            raise RuntimeError()
        kwargs['cargo_type'] = cargo_type

        if rent_type not in RENT_TYPE_ALL:
            raise RuntimeError()
        kwargs['rent_type'] = rent_type

        code, detail, long, lat = self.parse_locate(lct_depart)
        kwargs['lct_dpt_code'] = code
        kwargs['lct_dpt_detail'] = detail
        kwargs['lct_dpt_long'] = long
        kwargs['lct_dpt_lat'] = lat

        code, detail, long, lat = self.parse_locate(lct_dest)
        kwargs['lct_dst_code'] = code
        kwargs['lct_dst_detail'] = detail
        kwargs['lct_dst_long'] = long
        kwargs['lct_dst_lat'] = lat

        if not (tmlst[0] <= tmlst[1] < tmlst[2] <= tmlst[3]):
            raise RuntimeError()
        kwargs['tm_dpt_min'] = tmlst[0]
        kwargs['tm_dpt_max'] = tmlst[1]
        kwargs['tm_dst_min'] = tmlst[1]
        kwargs['tm_dst_max'] = tmlst[1]

        kwargs['loader_name'] = loader[0]
        kwargs['loader_phone'] = loader[1]
        kwargs['unloader_name'] = unloader[0]
        kwargs['unloader_phone'] = unloader[1]

        kwargs['cargo'] = cargo

    def parse_locate(self, location):
        region = location.get('region')
        if region is None:
            raise RuntimeError()
        code = data.LOCATIONS.get(tuple(region))
        if code is None:
            raise RuntimeError()
        detail = location.get('detail')
        longitude, latitude = location.get('coords')
        return code, detail, longitude, latitude

@bp_order.route('/new')
def order_new():
    print("order_new 000")
    dt = request.get_json(True)
    accid = dt.get('accid')
    orderinfo = dt.get('order')
    print("order_new 111 %s"%(accid))
    orderid = gen_order_id()
    new_order = IndentPool().add_new_order(accid, orderid, orderinfo)
    return jsonify(code=0, msg='success', data={'orderid':orderid})

@bp_order.route('/list')
def order_list():
    dt = request.get_json(True)
    page = dt.get('page')
    return IndentPool().show_orders(page)
