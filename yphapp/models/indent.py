from .. import db
import time
from flask import json
import datetime
import decimal


class IndentNum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process = db.Column(db.Integer)
    thread = db.Column(db.Integer)
    degree = db.Column(db.Integer)
    index = db.Column(db.Integer)

    def __init__(self, process, thread, degree, index):
        self.process = process
        self.thread = thread
        self.degree = degree
        self.index = index

    def __repr__(self):
        return '<IndentNum %d-%d>'%(self.process, self.thread)


class Indent(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    csgid = db.Column(db.Integer, db.ForeignKey('consignor.id'), nullable=False)
    tspid = db.Column(db.Integer, db.ForeignKey('transporter.id'), nullable=True)
    cargo_type = db.Column(db.SmallInteger)
    rent_type = db.Column(db.SmallInteger)
    price = db.Column(db.Integer)
    crttime = db.Column(db.TIMESTAMP)

    consignor = db.relationship('Consignor', uselist=False)
    transporter = db.relationship('Transporter', uselist=False)
    detail = db.relationship('IndentDetail', uselist=False)
    status = db.relationship('IndentStatus', uselist=False)
    cargo = db.relationship('IndentCargo', uselist=False)

    INNERPROP_TO_OUTTERNAME = {
        'id'            : ['orderid', True, None],
        'csgid'         : ['csgid', True, None],
        'tspid'         : ['tspid', False, None],
        'cargo_type'    : ['cargo_type', True, None],
        'rent_type'     : ['rent_type', True, None],
        'price'         : ['price', True, None],
        'crttime'       : ['crttime', True, None],
        'status'        : {
                            'status' : ['status', True, None],
                          },
        'detail'        : {
                            'dpt_lctcode'   : ['dpt_lctcode', True, None],
                            'dpt_lctdtl'    : ['dpt_lctdtl', True, None],
                            'dpt_lctlong'   : ['dpt_lctlong', True, None],
                            'dpt_lctlat'    : ['dpt_lctlat', True, None],
                            'dpt_tmclk'     : ['dpt_tmclk', True, None],
                            'dpt_tmload'    : ['dpt_tmload', True, None],
                            'dpt_ldrname'   : ['dpt_ldrname', True, None],
                            'dpt_ldrphone'  : ['dpt_ldrphone', True, None],
                            'dst_lctcode'   : ['dst_lctcode', True, None],
                            'dst_lctdtl'    : ['dst_lctdtl', True, None],
                            'dst_lctlong'   : ['dst_lctlong', True, None],
                            'dst_lctlat'    : ['dst_lctlat', True, None],
                            'dst_tmclk'     : ['dst_tmclk', True, None],
                            'dst_tmunload'  : ['dst_tmunload', True, None],
                            'dst_uldrname'  : ['dst_uldrname', True, None],
                            'dst_uldrphone' : ['dst_uldrphone', True, None],
                          },
        'cargo'         : {
                            'cargo'         : ['cargo', True, None],
                            'weight'        : ['weight', False, None],
                            'volume'        : ['volume', False, None],
                          },
    }

    def __init__(self, id, **kwargs):
        self.id = id
        self.detail = IndentDetail()
        self.status = IndentStatus()
        self.cargo = IndentCargo()
        if not kwargs:
            return
        for k, v in self.INNERPROP_TO_OUTTERNAME.items():
            if type(v) is list:
                name, force, default = v
                if name not in kwargs:
                    if force:
                        raise RuntimeError
                    else:
                        value = default
                else:
                    value = kwargs[name]
                setattr(self, k, value)
            if type(v) is dict:
                sub = getattr(self, k)
                for _k, _v in v.items():
                    name, force, default = _v
                    if name not in kwargs:
                        if force:
                            raise RuntimeError
                        else:
                            value = default
                    else:
                        value = kwargs[name]
                        if _k in ['dpt_tmclk', 'dst_tmclk']:
                            #value = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))
                            value = datetime.datetime.fromtimestamp(value)
                        elif _k == 'cargo':
                            value = json.dumps(value)
                        elif _k in ['dpt_lctlong', 'dpt_lctlat', 'dst_lctlong', 'dst_lctlat',]:
                            value = decimal.Decimal(value)
                    setattr(sub, _k, value)

    def SyncProp(self, dct):
        for k, v in self.INNERPROP_TO_OUTTERNAME.items():
            if type(v) is list:
                dct[v[0]] = getattr(self, k)
            if type(v) is dict:
                sub = getattr(self, k)
                for _k, _v in v.items():
                    value = getattr(sub, _k)
                    if _k in ['dpt_tmclk', 'dst_tmclk']:
                        value = int(time.mktime(value.timetuple()))
                    elif _k == 'cargo':
                        value = json.loads(value)
                    elif _k in ['dpt_lctlong', 'dpt_lctlat', 'dst_lctlong', 'dst_lctlat',]:
                        value = str(value)
                    dct[_v[0]] = value

    def __repr__(self):
        return '<Indent %s>'%str(self.id)


class IndentDetail(db.Model):
    id = db.Column(db.BigInteger, db.ForeignKey('indent.id'), primary_key=True)

    dpt_lctcode = db.Column(db.Integer)
    dpt_lctdtl = db.Column(db.String(50))
    dpt_lctlong = db.Column(db.DECIMAL(9, 6))
    dpt_lctlat = db.Column(db.DECIMAL(9, 6))
    dpt_tmclk = db.Column(db.TIMESTAMP)
    dpt_tmload = db.Column(db.Integer)
    dpt_ldrname = db.Column(db.String(20))
    dpt_ldrphone = db.Column(db.String(20))

    dst_lctcode = db.Column(db.Integer)
    dst_lctdtl = db.Column(db.String(50))
    dst_lctlong = db.Column(db.DECIMAL(9, 6))
    dst_lctlat = db.Column(db.DECIMAL(9, 6))
    dst_tmclk = db.Column(db.TIMESTAMP)
    dst_tmunload = db.Column(db.Integer)
    dst_uldrname = db.Column(db.String(20))
    dst_uldrphone = db.Column(db.String(20))

    def __repr__(self):
        return '<IndentDetail %s>'%str(self.id)


class IndentStatus(db.Model):
    id = db.Column(db.BigInteger, db.ForeignKey('indent.id'), primary_key=True)
    status = db.Column(db.SmallInteger)

    def __repr__(self):
        return '<IndentStatus %s>'%str(self.id)


class IndentCargo(db.Model):
    id = db.Column(db.BigInteger, db.ForeignKey('indent.id'), primary_key=True)
    cargo = db.Column(db.String(200))
    weight = db.Column(db.Integer)
    volume = db.Column(db.Integer)

    def __repr__(self):
        return '<IndentCargo %s>'%str(self.id)
