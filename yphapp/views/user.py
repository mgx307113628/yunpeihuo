from flask import Blueprint, request, jsonify
from .. import app, db
from ..models import user
import datetime
from ..define import *

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
    #    account.transporter = user.Transporter()
    #elif role == ROLE_TYPE_CSGN:
    #    account.consignor = user.Consignor()
    #elif role == ROLE_TYPE_CONV:
    #    pass
    #else:
    #    pass
    #account.crtplat = plat
    #account.crtrole = role
    print("user_register 111 %s %s"%(acc, pwd))
    if user.Account.query.filter_by(acc=acc).first():
        return jsonify(code=1, msg='fail', data={'account':acc})
    account = user.Account(acc, pwd)
    account.crtip = ip
    account.crtmac = mac
    account.crttime = datetime.datetime.now()
    db.session.add(account)
    account.transporter = user.Transporter()#TODO
    account.consignor = user.Consignor()#TODO
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
    #    account.transporter = user.Transporter()
    #elif role == ROLE_TYPE_CSGN:
    #    account.consignor = user.Consignor()
    #elif role == ROLE_TYPE_CONV:
    #    pass
    #else:
    #    pass
    #account.crtplat = plat
    #account.crtrole = role
    print("user_login %s %s"%(acc, pwd))
    account = user.Account.query.filter_by(acc=acc, pwd=pwd).one()
    account.lastip = ip
    account.lastmac = mac
    account.lasttime = datetime.datetime.now()
    db.session.commit()
    print("user_login %s %s: %d"%(acc, pwd, account.id))
    return jsonify(code=0, msg='success', data={'id':account.id, 'account':acc})

@bp_user.route('/setinfo', methods=['POST'])
def user_setinfo():
    print("user_setinfo 000")
    data = request.get_json(True)
    accid = int(data.get('accid'))
    account = user.Account.query.filter_by(id=accid).one()
    role = int(data.get('role'))
    dt = data.get('data')
    if 'name' in dt:
        account.name = dt['name']
    if 'sex' in dt:
        account.sex = dt['sex']
    if 'idno' in dt:
        account.idno = dt['idno']
    if 'phone' in dt:
        account.phone = dt['phone']
    if role == ROLE_TYPE_TRSP:
        if 'd_lic' in dt:
            account.transporter.d_lic = dt['d_lic']
        if 'v_lic' in dt:
            account.transporter.v_lic = dt['v_lic']
    db.session.commit()
    print("user_setinfo %d %d %s"%(accid, role, dt))
    return jsonify(code=0, msg='success')

@bp_user.route('/getinfo', methods=['POST'])
def user_getinfo():
    print("user_getinfo 000")
    data = request.get_json(True)
    accid = int(data.get('accid'))
    account = user.Account.query.filter_by(id=accid).one()
    role = int(data.get('role'))
    dt = data.get('data')
    r = {}
    for p in dt:
        if p in ('d_lic', 'v_lic'):
            r[p] = getattr(account.transporter, p, None)
        else:
            r[p] = getattr(account, p, None)
    print("user_getinfo %d %d %s"%(accid, role, dt))
    return jsonify(code=0, msg='success', data=r)
