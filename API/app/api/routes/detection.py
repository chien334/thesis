from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.detection import DetectionHistory
import json
import os
from werkzeug.utils import secure_filename

detection_bp = Blueprint('detection', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@detection_bp.route('/history', methods=['GET'])
@jwt_required()
def get_detection_history():
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    history = DetectionHistory.query.filter_by(user_id=current_user.id)\
        .order_by(DetectionHistory.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'history': [item.to_dict() for item in history.items],
        'total': history.total,
        'pages': history.pages,
        'current_page': history.page
    })

@detection_bp.route('/detect', methods=['POST'])
@jwt_required()
def detect_image():
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400
    
    # Create uploads directory if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # Save the file
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        # Here you would call your detection model
        # For now, we'll just create a dummy result
        result = {
            "detections": [
                {"class": "example", "confidence": 0.95}
            ]
        }
        
        # Save to history
        history_item = DetectionHistory(
            user_id=current_user.id,
            image_path=filepath,
            result=json.dumps(result)
        )
        db.session.add(history_item)
        db.session.commit()
        
        return jsonify({
            "detection_id": history_item.id,
            "result": result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@detection_bp.route('/history/<int:history_id>', methods=['GET'])
@jwt_required()
def get_detection_item(history_id):
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    history_item = DetectionHistory.query.filter_by(
        id=history_id,
        user_id=current_user.id
    ).first_or_404()
    
    return jsonify(history_item.to_dict())

@detection_bp.route('/history/<int:history_id>', methods=['DELETE'])
@jwt_required()
def delete_detection_item(history_id):
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    history_item = DetectionHistory.query.filter_by(
        id=history_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Delete the image file if it exists
    if os.path.exists(history_item.image_path):
        os.remove(history_item.image_path)
    
    db.session.delete(history_item)
    db.session.commit()
    
    return jsonify({"message": "Detection history item deleted successfully"}) 