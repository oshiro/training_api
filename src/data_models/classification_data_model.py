from .db import db

class ClassificationData(db.Model):
    model_id = db.Column(db.String(100), primary_key=True)
    sepal_length = db.Column(db.Float, nullable=False)
    sepal_width = db.Column(db.Float, nullable=False)
    petal_length = db.Column(db.Float, nullable=False)
    petal_width = db.Column(db.Float, nullable=False)
    predicted_class_id = db.Column(db.Integer, nullable=False)
    predicted_class = db.Column(db.String(15), nullable=False)