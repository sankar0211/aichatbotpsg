from flask import Blueprint, render_template, request, jsonify, Response, redirect, url_for
from flask_login import login_required, current_user
from app.models import ChatSession, ChatMessage
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app import db
import json

chat_bp = Blueprint('chat', __name__)

# Ensure FAISS index is built before any chat requests
@chat_bp.before_app_request
def initialize_rag():
    if not rag_service.faq_list:
        rag_service.build_index()

@chat_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('chat.chat'))
    return redirect(url_for('auth.login'))

@chat_bp.route('/chat')
@login_required
def chat():
    # Find or create a session for the user
    session = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).first()
    if not session:
        session = ChatSession(user_id=current_user.id)
        db.session.add(session)
        db.session.commit()
        
    return render_template('chat/index.html', session_id=session.id, user=current_user)

@chat_bp.route('/api/chat/history/<int:session_id>')
@login_required
def chat_history(session_id):
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
    messages = ChatMessage.query.filter_by(session_id=session.id).order_by(ChatMessage.timestamp.asc()).all()
    
    return jsonify([
        {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp.isoformat()}
        for msg in messages
    ])

@chat_bp.route('/api/chat/stream', methods=['POST'])
@login_required
def chat_stream():
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id')
    
    if not user_message or not session_id:
        return jsonify({"error": "Missing message or session_id"}), 400
        
    # Verify session belongs to user
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()

    def generate():
        for chunk in llm_service.generate_response_stream(session_id, user_message):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
        
    return Response(generate(), mimetype='text/event-stream')
