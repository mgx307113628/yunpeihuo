from .. import db


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

    consignor = db.relationship('Consignor', uselist=False)
    transporter = db.relationship('Transporter', uselist=False)
    detail = db.relationship('IndentDetail', uselist=False)
    status = db.relationship('IndentStatus', uselist=False)
    cargo = db.relationship('IndentCargo', uselist=False)

    def __init__(self, id, csgid, **kwargs):
        self.id = id
        self.csgid = csgid
        self.detail = IndentDetail()
        self.status = IndentStatus()
        self.cargo = IndentCargo()
        for k, v in kwargs.pop('detail', {}).items():
            setattr(self.detail, k, v)
        for k, v in kwargs.pop('status', {}).items():
            setattr(self.status, k, v)
        for k, v in kwargs.pop('cargo', {}).items():
            setattr(self.cargo, k, v)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<Indent %s>'%str(self.id)


class IndentDetail(db.Model):
    id = db.Column(db.BigInteger, db.ForeignKey('indent.id'), primary_key=True)

    dpt_lctcode = db.Column(db.Integer)
    dpt_lctdtl = db.Column(db.String(50))
    dpt_lctlong = db.Column(db.Float)
    dpt_lctlat = db.Column(db.Float)
    dpt_tmclk = db.Column(db.TIMESTAMP)
    dpt_tmload = db.Column(db.Integer)
    dpt_ldrname = db.Column(db.String(20))
    dpt_ldrphone = db.Column(db.String(20))

    dst_lctcode = db.Column(db.Integer)
    dst_lctdtl = db.Column(db.String(50))
    dst_lctlong = db.Column(db.Float)
    dst_lctlat = db.Column(db.Float)
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
