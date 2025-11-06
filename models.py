from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    requester_name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    vendor_name = db.Column(db.String(100), nullable=False)
    vat_id = db.Column(db.String(50), nullable=False)
    commodity_group = db.Column(db.String(100), nullable=False)
    total_cost = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    action = db.Column(db.Integer, nullable=False)
    
    order_lines = db.relationship('OrderLine', backref='request', cascade='all, delete-orphan')
    
class OrderLine(db.Model):
    __tablename__ = 'order_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"), nullable=False)
    position_description = db.Column(db.String(200), nullable=False)
    unit_price = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(50))
    total_price = db.Column(db.String(100), nullable=False)
    