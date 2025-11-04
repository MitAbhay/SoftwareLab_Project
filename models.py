from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class CropRecord(db.Model):
    __tablename__ = 'dataset'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # ✅ synthetic PK
    
    location = db.Column(db.String)
    soil_type = db.Column(db.String)
    Crop = db.Column(db.String)
    season = db.Column(db.String)
    sow_date = db.Column(db.DateTime)
    harvest_date = db.Column(db.DateTime)
    area_ha = db.Column(db.Float)
    pH = db.Column('pH', db.Float)
    Rainfall = db.Column(db.Float)
    Temperature = db.Column(db.Float)
    Humidity = db.Column(db.Float)

class AttributeInfo(db.Model):
    __tablename__ = 'attributes'
    Attribute = db.Column(db.String, primary_key=True)
    Full_Form___Description = db.Column(db.String)
    # original file had an extra empty column named Unnamed:_2 - ignore for now

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    id = db.Column(db.Integer, primary_key=True)
    crop = db.Column(db.String)
    expected_roi = db.Column(db.Float)
    sowing_date = db.Column(db.Date)
    harvest_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
