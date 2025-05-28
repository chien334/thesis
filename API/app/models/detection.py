from app import db
from datetime import datetime

class DetectionHistory(db.Model):
    __tablename__ = 'detection_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    result = db.Column(db.Text, nullable=False)  # JSON string of detection results
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('detection_history', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_path': self.image_path,
            'result': self.result,
            'created_at': self.created_at.isoformat()
        } 