from flask import Blueprint, request, jsonify
from .. import app, db
from ..models import mdaccount

bp_user = Blueprint('user', __name__) 

@bp_user.route('/register')
def user_register():
    print("user_register 000")
    data = request.get_json(True)
    acc = data.get('account')
    pwd = data.get('password')
    print("user_register 111 %s %s"%(acc, pwd))
    account = mdaccount.Account(acc, pwd)
    account.transporter = mdaccount.Transporter()
    db.session.add(account)
    #db.session.add(transporter)
    db.session.commit()
    print("user_register 222 %s %s %d"%(acc, pwd, account.id))
    return jsonify(code=0, msg='success', data={'id':account.id, 'account':acc})

@bp_user.route('/query')
def user_query():
    account = mdaccount.Account.query.filter_by(acc='acc_aaabbb').one()
    print(account)
    print(account.transporter)
    print(account.consignor)
    return jsonify(code=0, msg='success', data={'id':account.id, 'account':account.acc})

@bp_user.route('/login')
def user_login():
    print("user_login 000")
    data = request.get_json(True)
    acc = data.get('account')
    pwd = data.get('password')
    print("user_login %s %s"%(acc, pwd))
    account = mdaccount.Account.query.filter_by(acc=acc, pwd=pwd).one()
    print("user_login %s %s: %d"%(acc, pwd, account.id))
    return jsonify(code=0, msg='success', data={'id':account.id, 'account':acc})
