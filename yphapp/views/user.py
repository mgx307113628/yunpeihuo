from flask import Blueprint, request, jsonify
from .. import app, db
from ..models import md_account

bp_user = Blueprint('user', __name__) 

@bp_user.route('/register', methods=['POST'])
def user_register():
    print("user_register 000")
    data = request.get_json(True)
    acc = data.get('account')
    pwd = data.get('password')
    print("user_register 111 %s %s"%(acc, pwd))
    account = md_account.Account(acc, pwd)
    account.transporter = md_account.Transporter()
    db.session.add(account)
    #db.session.add(transporter)
    db.session.commit()
    print("user_register 222 %s %s %d"%(acc, pwd, account.id))
    return jsonify(code=0, msg='success', data={'id':account.id, 'account':acc})

@bp_user.route('/query', methods=['POST']) #TODO 上线删除
def user_query():
    data = request.get_json(True)
    acc = data.get('account')
    account = md_account.Account.query.filter_by(acc=acc).one()
    return jsonify(code=0, msg='success', data={'id':account.id, 'account':account.acc, 'password':account.pwd})

@bp_user.route('/login', methods=['POST'])
def user_login():
    print("user_login 000")
    data = request.get_json(True)
    acc = data.get('account')
    pwd = data.get('password')
    print("user_login %s %s"%(acc, pwd))
    account = md_account.Account.query.filter_by(acc=acc, pwd=pwd).one()
    print("user_login %s %s: %d"%(acc, pwd, account.id))
    return jsonify(code=0, msg='success', data={'id':account.id, 'account':acc})
