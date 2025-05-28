from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.chat import Chat, ChatMessage
import json

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('', methods=['POST'])
@jwt_required()
def create_chat():
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    data = request.get_json()
    
    chat = Chat(
        user_id=current_user.id,
        title=data.get('title', 'New Chat')
    )
    db.session.add(chat)
    db.session.commit()
    
    return jsonify(chat.to_dict()), 201

@chat_bp.route('', methods=['GET'])
@jwt_required()
def get_chats():
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    chats = Chat.query.filter_by(user_id=current_user.id)\
        .order_by(Chat.updated_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'chats': [chat.to_dict() for chat in chats.items],
        'total': chats.total,
        'pages': chats.pages,
        'current_page': chats.page
    })

@chat_bp.route('/<int:chat_id>', methods=['GET'])
@jwt_required()
def get_chat(chat_id):
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
    
    messages = ChatMessage.query.filter_by(chat_id=chat_id)\
        .order_by(ChatMessage.created_at.asc())\
        .all()
    
    return jsonify({
        'chat': chat.to_dict(),
        'messages': [message.to_dict() for message in messages]
    })

@chat_bp.route('/<int:chat_id>/messages', methods=['POST'])
@jwt_required()
def add_message(chat_id):
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
    
    data = request.get_json()
    message = ChatMessage(
        chat_id=chat_id,
        role=data['role'],
        content=data['content']
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify(message.to_dict()), 201

@chat_bp.route('/<int:chat_id>', methods=['PUT'])
@jwt_required()
def update_chat(chat_id):
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
    
    data = request.get_json()
    if 'title' in data:
        chat.title = data['title']
    
    db.session.commit()
    return jsonify(chat.to_dict())

@chat_bp.route('/<int:chat_id>', methods=['DELETE'])
@jwt_required()
def delete_chat(chat_id):
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(chat)
    db.session.commit()
    
    return jsonify({"message": "Chat deleted successfully"}) 