from flask import Blueprint, request, jsonify
from .. import app, db
from ..models import md_account
import datetime

bp_user = Blueprint('user', __name__) 

@bp_user.route('/register', methods=['POST'])
def user_register():
    print("user_register 000")
    data = request.get_json(True)
    acc = data.get('account')
    pwd = data.get('password')
    ip = data.get('ip')
    mac = data.get('mac')
    #TODO
    #plat = int(data.get('platform'))
    #role = int(data.get('role'))
    #if plat not in [PLAT_TYPE_APP, APP PLAT_TYPE_WEB]:
    #    raise RuntimeError
    #if role not in [ROLE_TYPE_NONE, ROLE_TYPE_TRSP, ROLE_TYPE_CSGN, ROLE_TYPE_CONV,]:
    #    raise RuntimeError
    #if role == ROLE_TYPE_TRSP:
    #    account.transporter = md_account.Transporter()
    #elif role == ROLE_TYPE_CSGN:
    #    account.consignor = md_account.Consignor()
    #elif role == ROLE_TYPE_CONV:
    #    pass
    #else:
    #    pass
    #account.crtplat = plat
    #account.crtrole = role
    print("user_register 111 %s %s"%(acc, pwd))
    if md_account.Account.query.filter_by(acc=acc).first():
        return jsonify(code=1, msg='fail', data={'account':acc})
    account = md_account.Account(acc, pwd)
    account.crtip = ip
    account.crtmac = mac
    account.crttime = datetime.datetime.now()
    db.session.add(account)
    account.transporter = md_account.Transporter()#TODO
    account.consignor = md_account.Consignor()#TODO
    db.session.commit()
    print("user_register 222 %s %s %d %s %s"%(acc, pwd, account.id, account.transporter, account.consignor))
    return jsonify(code=0, msg='success', data={'id':account.id, 'account':acc})


@bp_user.route('/login', methods=['POST'])
def user_login():
    print("user_login 000")
    data = request.get_json(True)
    acc = data.get('account')
    pwd = data.get('password')
    ip = data.get('ip')
    mac = data.get('mac')
    #TODO
    #plat = int(data.get('platform'))
    #role = int(data.get('role'))
    #if plat not in [PLAT_TYPE_APP, APP PLAT_TYPE_WEB]:
    #    raise RuntimeError
    #if role not in [ROLE_TYPE_NONE, ROLE_TYPE_TRSP, ROLE_TYPE_CSGN, ROLE_TYPE_CONV,]:
    #    raise RuntimeError
    #if role == ROLE_TYPE_TRSP:
    #    account.transporter = md_account.Transporter()
    #elif role == ROLE_TYPE_CSGN:
    #    account.consignor = md_account.Consignor()
    #elif role == ROLE_TYPE_CONV:
    #    pass
    #else:
    #    pass
    #account.crtplat = plat
    #account.crtrole = role
    print("user_login %s %s"%(acc, pwd))
    account = md_account.Account.query.filter_by(acc=acc, pwd=pwd).one()
    account.lastip = ip
    account.lastmac = mac
    account.lasttime = datetime.datetime.now()
    db.session.commit()
    print("user_login %s %s: %d"%(acc, pwd, account.id))
    return jsonify(code=0, msg='success', data={'id':account.id, 'account':acc})
