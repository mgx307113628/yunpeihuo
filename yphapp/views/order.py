import threading
from flask import Blueprint, request, jsonify
from .. import app, db
from ..models import md_indent
from werkzeug.local import Local
import time

bp_order = Blueprint('order', __name__) 

order_cnt = Local()


def gen_order_id():
    """
    :return:订单号.最大值为18446744073709551615
            订单号存于MYSQL的BIGINT
            BIGINT无符号数范围：0~18446744073709551615
    """
    tname = threading.current_thread().name
    if type(tname) is bytes:
        tname = str(tname, encoding='utf8')
    #用uwsgi启动,最多线程数为10个: uWSGIWorker1Core0
    if tname[:11] == 'uWSGIWorker1Core0' and tname[12:16] == 'Core':
        tid = tname[11] + str(int(tname[16])+1)
    #测试:用python启动
    elif tname == 'MainThread':
        tid = '00'
    elif tname[:7] == 'Thread-':
        tid = '0%s'%tname[7]
    else:
        raise RuntimeError()

    now = int(time.time() * 1000) % 1000000000000 #只能使用约31年,31年后可能会出现订单号重复

    tm, num = getattr(order_cnt, 'same_time_count', [0,0])
    if now == tm:
        num += 1
    else:
        num = 1
    setattr(order_cnt, 'same_time_count', [now,num])

    return int('1%s%d%.2d'%(tid, now, num)) #17位

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
