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

class IndentPool:
    _instance = None
    _initflag = False
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if IndentPool._initflag == False:
            IndentPool._initflag = True
            self.indents_dct = {}
            self.indents_lst = []
            self.update = False

    def init_pool(self):
        for indent in md_indent.Indent.query.all():
            self.indents_dct[indent.id] = indent
            self.indents_lst.append(indent)
        print(id(self.indents_lst))
        return

    def add_new_order(self, accid, orderid, orderinfo):
        kwargs = {}
        self.decode_order(kwargs, orderinfo)
        indent = md_indent.Indent(orderid, accid, **kwargs)
        db.session.add(indent)
        db.session.commit()
        self.indents_dct[orderid] = indent
        self.indents_lst.append(indent)
        self.update = True

    def show_orders(self, current, num):
        sendlst = []
        send = False
        n = 0
        if current == 0:
            send = True
        for idx, indent in enumerate(self.indents_lst):
            if send == True:
                sendlst.append(self.encode_order(indent))
                n += 1
                if n >= num:
                    break
            elif idx+1 == current:
                send = True
        self.indents_dct = {}
        self.indents_lst = []
        return jsonify(code=0, msg='success', data={'orders':sendlst})

    def encode_order(self, indent):
        data = {}
        data['orderid'] = str(indent.id)
        data['status'] = indent.status.status
        data['cargo_type'] = indent.cargo_type
        data['rent_type'] = indent.rent_type
        data['lct_depart'] = self.encode_locate(
                                    indent.detail.dpt_lctcode,
                                    indent.detail.dpt_lctdtl,
                                    indent.detail.dpt_lctlong,
                                    indent.detail.dpt_lctlat,)
        data['lct_dest'] = self.encode_locate(
                                    indent.detail.dst_lctcode,
                                    indent.detail.dst_lctdtl,
                                    indent.detail.dst_lctlong,
                                    indent.detail.dst_lctlat,)
        data['times'] = [
            #int(time.mktime(time.strptime(indent.detail.dpt_tmclk,'%Y-%m-%d %H:%M:%S'))),
            int(time.mktime(indent.detail.dpt_tmclk.timetuple())),
            indent.detail.dpt_tmload,
            #int(time.mktime(time.strptime(indent.detail.dst_tmclk,'%Y-%m-%d %H:%M:%S'))),
            int(time.mktime(indent.detail.dst_tmclk.timetuple())),
            indent.detail.dst_tmunload,]
        data['loader'] = [ indent.detail.dpt_ldrname, indent.detail.dpt_ldrphone,]
        data['unloader'] = [ indent.detail.dst_uldrname, indent.detail.dst_uldrphone,]
        data['cargo'] = json.loads(indent.cargo.cargo)
        return data

    def decode_order(self, kwargs, info):
        status = info.get('status')
        cargo_type = info.get('cargo_type')
        rent_type = info.get('rent_type')
        lct_depart = info.get('lct_depart')
        lct_dest = info.get('lct_dest')
        tmlst = info.get('times')
        loader = info.get('loader')
        unloader = info.get('unloader')
        cargo = info.get('cargo')

        dtl = kwargs.setdefault('detail', {})
        st = kwargs.setdefault('status', {})
        cg = kwargs.setdefault('cargo', {})

        st['status'] = status

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

        code, detail, long, lat = self.decode_locate(lct_depart)
        dtl['dpt_lctcode'] = code
        dtl['dpt_lctdtl'] = detail
        dtl['dpt_lctlong'] = long
        dtl['dpt_lctlat'] = lat

        code, detail, long, lat = self.decode_locate(lct_dest)
        dtl['dst_lctcode'] = code
        dtl['dst_lctdtl'] = detail
        dtl['dst_lctlong'] = long
        dtl['dst_lctlat'] = lat

        #if not (tmlst[0] <= tmlst[1] < tmlst[2] <= tmlst[3]):
        #    raise RuntimeError()
        dtl['dpt_tmclk'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tmlst[0]))
        dtl['dpt_tmload'] = tmlst[1]
        dtl['dst_tmclk'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tmlst[2]))
        dtl['dst_tmunload'] = tmlst[3]

        dtl['dpt_ldrname'] = loader[0]
        dtl['dpt_ldrphone'] = loader[1]
        dtl['dst_uldrname'] = unloader[0]
        dtl['dst_uldrphone'] = unloader[1]

        cg['cargo'] = json.dumps(cargo)

    def decode_locate(self, location):
        region = location.get('region')
        if region is None:
            raise RuntimeError()
        code = data.LOCATION_CODE.get(tuple(region))
        if code is None:
            raise RuntimeError()
        detail = location.get('detail')
        longitude, latitude = location.get('coords')
        return code, detail, longitude, latitude

    def encode_locate(self, code, detail, longitude, latitude):
        dct = {}
        dct['region'] = data.CODE_LOCATION.get(code)
        dct['detail'] = detail
        dct['coords'] = [longitude, latitude]
        return dct
    
    def take_order(self, accid, orderid):
        indent = md_indent.query.filter_by(id=orderid).one()
        indent.tspid = accid
        db.session.commit()
        return jsonify(code=0, msg='success', data={'orderid':orderid})


@bp_order.route('/new', methods=['POST'])
def order_new():
    print("order_new 000")
    dt = request.get_json(True)
    accid = dt.get('accid')
    orderinfo = dt.get('order')
    orderinfo['status'] = INDENT_STATUS_PUBLISHING 
    print("order_new 111 %s"%(accid))
    orderid = gen_order_id()
    new_order = IndentPool().add_new_order(accid, orderid, orderinfo)
    return jsonify(code=0, msg='success', data={'orderid':str(orderid)})

@bp_order.route('/list', methods=['POST'])
def order_list():
    print('order_list 111111111111111')
    IndentPool().init_pool()
    dt = request.get_json(True)
    current = int(dt.get('current', 0))
    num = int(dt.get('num'))
    return IndentPool().show_orders(current, num)

@bp_order.route('/take', methods=['POST'])
def order_take():
    print('order_take 111111111111111')
    IndentPool().init_pool()
    dt = request.get_json(True)
    accid = int(dt.get('accid'))
    orderid = int(dt.get('orderid'))
    return IndentPool().take_order(accid, orderid)
