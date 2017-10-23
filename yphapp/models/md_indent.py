from .. import db


class Indent(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    csgid = db.Column(db.Integer, db.ForeignKey('consignor.id'))

    consignor = db.relationship('Consignor', uselist=False)

    def __init__(self, id, csgid):
        self.id = id
        self.csgid = csgid

    def __repr__(self):
        return '<Indent %s>'%str(self.id)


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
