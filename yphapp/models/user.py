from .. import db


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    acc = db.Column(db.String(50), unique=True)#TODO 调整长度
    pwd = db.Column(db.String(50))#TODO 调整长度
    crttime = db.Column(db.TIMESTAMP)
    crtip = db.Column(db.String(50))
    crtmac = db.Column(db.String(50))
    crtplat = db.Column(db.SmallInteger)
    crtrole = db.Column(db.SmallInteger)
    name = db.Column(db.String(20))
    idno = db.Column(db.String(20))
    lasttime = db.Column(db.TIMESTAMP)
    lastip = db.Column(db.String(50))
    lastmac = db.Column(db.String(50))
    lastplat = db.Column(db.SmallInteger)
    lastrole = db.Column(db.SmallInteger)

    transporter = db.relationship('Transporter', uselist=False)
    consignor = db.relationship('Consignor', uselist=False)

    def __init__(self, acc, pwd):
        self.acc = acc
        self.pwd = pwd

    def __repr__(self):
        return '<Account %s %s>'%(str(self.id), self.acc)


class Transporter(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)

    account = db.relationship('Account', uselist=False)

    def __init__(self):
        pass

    def __repr__(self):
        return '<Transporter %s>'%str(self.id)


class Consignor(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)

    account = db.relationship('Account', uselist=False)
    indents = db.relationship('Indent', lazy='dynamic')

    def __init__(self):
        pass

    def __repr__(self):
        return '<Consignor %s>'%str(self.id)


class Convoy(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)

    account = db.relationship('Account', uselist=False)

    def __init__(self):
        pass

    def __repr__(self):
        return '<Convoy %s>'%str(self.id)
