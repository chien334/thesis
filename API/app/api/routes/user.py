from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.utils.security import verify_password, get_password_hash
from functools import wraps

user_bp = Blueprint('user', __name__)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user = User.query.filter_by(email=get_jwt_identity()).first()
        if not current_user or not current_user.is_admin:
            return jsonify({"error": "Admin privileges required"}), 403
        return fn(*args, **kwargs)
    return wrapper

@user_bp.route('/token', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(email=username).first()
    if not user:
        user = User.query.filter_by(username=username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=user.email)
    return jsonify({
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    })

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already taken"}), 400
    
    user = User(
        email=data['email'],
        username=data['username'],
        hashed_password=get_password_hash(data['password'])
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    return jsonify(current_user.to_dict())

@user_bp.route('/admin/list', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    users = query.paginate(page=page, per_page=per_page)
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': users.page
    })

@user_bp.route('/admin/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already registered"}), 400
        user.email = data['email']
    
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already taken"}), 400
        user.username = data['username']
    
    if 'password' in data:
        user.hashed_password = get_password_hash(data['password'])
    
    if 'is_admin' in data:
        user.is_admin = data['is_admin']
    
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/admin/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}) 