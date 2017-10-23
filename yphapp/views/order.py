import threading
from flask import Blueprint, request, jsonify
from .. import app, db
from ..models import md_indent
from werkzeug.local import Local
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

@bp_order.route('/new')
def order_new():
    print("order_new 000")
    #data = request.get_json(True)
    #accid = data.get('accid')
    #print("order_new 111 %s"%(accid))
    orderid = gen_order_id()
    return jsonify(code=0, msg='success', data={'orderid':orderid})
    #account = md_account.Account(acc, pwd)
    #account.transporter = md_account.Transporter()
    #db.session.add(account)
    #db.session.commit()
    #print("order_new 222 %s %s %d"%(acc, pwd, account.id))
    #return jsonify(code=0, msg='success', data={'id':account.id, 'account':acc})
