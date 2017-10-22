import threading
from flask import Blueprint, request, jsonify
from .. import app, db
from ..models import md_indent
from werkzeug import Local

bp_order = Blueprint('order', __name__) 

thread_list = []
thread_list_lock = threading.Lock()
order_cnt = Local()

def GetIndent():
    now = int(time.time()*1000)%1000000000000

    threadid = threading.current_thread().ident
    thread_list_lock.acquire()#TODO 加try
    if threadid not in thread_list:
        thread_list.apppend(thread_list)
    idx = thread_list.index(threadid)
    thread_list_lock.release()

    tm, num = getattr(order_cnt, 'same_time_count', [0,0])
    if now == tm:
        d[1] = num = num + 1
    else:
        d[0] = now
        d[1] = num = 1

@bp_order.route('/new')
def order_new():
    print("order_new 000")
    data = request.get_json(True)
    acc = data.get('account')
    pwd = data.get('password')
    print("order_new 111 %s %s"%(acc, pwd))
    #account = md_account.Account(acc, pwd)
    #account.transporter = md_account.Transporter()
    #db.session.add(account)
    #db.session.commit()
    print("order_new 222 %s %s %d"%(acc, pwd, account.id))
    return jsonify(code=0, msg='success', data={'id':account.id, 'account':acc})
