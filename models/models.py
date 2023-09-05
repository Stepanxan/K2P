from app import db
from datetime import datetime
from sqlalchemy.orm import relationship


class Batch(db.Model):
    __tablename__ = 'batches'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    arrival_date = db.Column(db.Date, nullable=False)

    product = relationship("Product", back_populates="batches")

    def __init__(self, product_id, quantity, arrival_date):
        self.product_id = product_id
        self.quantity = quantity
        self.arrival_date = arrival_date
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    added_date = db.Column(db.Date, nullable=True, default=datetime.utcnow)

    batches = relationship("Batch", back_populates="product")

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    expense_date = db.Column(db.Date, nullable=True)



