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
