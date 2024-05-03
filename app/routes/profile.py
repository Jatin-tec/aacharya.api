from flask import Blueprint, render_template, session, current_app, jsonify, request
from ..services.auth_service import login_required, get_user_info
from bson.objectid import ObjectId

bp = Blueprint('profile', __name__, url_prefix='/dashboard')

@bp.route('/')
def profile():
    try:
        # Get the user's identity from the JWT
        
        # Establish a connection to the users collection
        db_users = current_app.db["users"]
        topics = current_app.db["topics"]

        user_id = get_user_info().get("sub")
        print(user_id)
        # Convert learningTopics string IDs to ObjectId
        user = db_users.find_one({"sub": user_id})

        if not user:
            return jsonify({"error": "User not found"}), 404

        learningTopics = topics.find({"sub": user_id})

        learned_topics_details = []
        for topic in learningTopics:
            learned_topics_details.append(topic)
        print(learned_topics_details, "learned_topics_details")
        # Render the dashboard page with the user and topics information
        return render_template('dashboard.html', user_info=user, topics=learned_topics_details)
    
    except Exception as e:
        # Handle exceptions such as connection errors or bad data
        current_app.logger.error(f"Error fetching profile: {e}")
        return jsonify({"error": "An error occurred while fetching the profile"}), 500

@bp.route('/watch-history')
def history():
    if request.method == 'GET':
        pass
    if request.method == 'POST':
        db_videos = current_app.db["videos"]
            