from .. import db


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    acc = db.Column(db.String(20), unique=True)
    pwd = db.Column(db.String(20))

    transporter = db.relationship('Transporter', uselist=False)
    consignor = db.relationship('Consignor', uselist=False)

    def __init__(self, acc, pwd):
        self.acc = acc
        self.pwd = pwd

    def __repr__(self):
        return '<Account %s>'%self.acc


class Transporter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accid = db.Column(db.Integer, db.ForeignKey('account.id'))

    account = db.relationship('Account', uselist=False)

    def __init__(self):
        pass

    def __repr__(self):
        if getattr(self, 'account'):
            return '<Transporter %s>'%self.account
        else:
            return '<Transporter orphan %d>'%self.id


class Consignor(db.Model):
    #cargo
    id = db.Column(db.Integer, primary_key=True)
    accid = db.Column(db.Integer, db.ForeignKey('account.id'))

    account = db.relationship('Account', uselist=False)

    def __init__(self):
        pass

    def __repr__(self):
        if getattr(self, 'account'):
            return '<Consignor %s>'%self.account
        else:
            return '<Consignor orphan %d>'%self.id
