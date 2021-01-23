from . import db

class ExemplaryModel(db.Model):
    __tablename__ = 'testable-models'

    id = db.Column(db.Integer, primary_key=True)
    string_field = db.Column(db.String(64), unique=False, nullable=False)
    integer_field = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, id, string_field, integer_field):
        self.id = id
        self.string_field = string_field
        self.integer_field = integer_field

    def __repr__(self):
        return '<TestableModel {0}>'.format(self.id)

# creating tables in db
# db.create_all()