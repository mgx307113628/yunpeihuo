from .. import db


class Indent(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    csgid = db.Column(db.Integer, db.ForeignKey('consignor.id'), nullable=False)
    tspid = db.Column(db.Integer, db.ForeignKey('transporter.id'), nullable=True)
    cargo_type = db.Column(db.SmallInteger)
    rent_type = db.Column(db.SmallInteger)
    status = db.Column(db.SmallInteger)
    price = db.Column(db.Integer)

    lct_dpt_code = db.Column(db.Integer)
    lct_dpt_detail = db.Column(db.String(50))
    lct_dpt_long = db.Column(db.Float)
    lct_dpt_lat = db.Column(db.Float)
    lct_dst_code = db.Column(db.Integer)
    lct_dst_detail = db.Column(db.String(50))
    lct_dst_long = db.Column(db.Float)
    lct_dst_lat = db.Column(db.Float)
    tm_dpt_min = db.Column(db.TIMESTAMP)
    tm_dpt_max = db.Column(db.TIMESTAMP)
    tm_dst_min = db.Column(db.TIMESTAMP)
    tm_dst_max = db.Column(db.TIMESTAMP)
    loader_name = db.Column(db.String(20))
    loader_phone = db.Column(db.String(20))
    unloader_name = db.Column(db.String(20))
    unloader_phone = db.Column(db.String(20))
    cargo = db.Column(db.String(200))
    weight = db.Column(db.Integer)
    volume = db.Column(db.Integer)

    consignor = db.relationship('Consignor', uselist=False)
    transporter = db.relationship('Transporter', uselist=False)

    def __init__(self, id, csgid, **kwargs):
        self.id = id
        self.csgid = csgid
        for k, v in kwargs.items():
            setattr(self, k, v)

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

