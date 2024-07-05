from flask import Blueprint, current_app, jsonify, request
from bson.objectid import ObjectId
from ..services.chat_service import huggingface_ef
from ..services.auth_service import get_user_by_email
from flask_jwt_extended import jwt_required, get_jwt_identity


bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/', methods=['GET', 'POST'], endpoint='profile_view')
@jwt_required( )
def profile_view():
    # Establish a connection to the collections
    notes_collection = current_app.db["notes"]
    watch_history_collection = current_app.db["watch_history"]
    videos_collection = current_app.db["videos"]
    topics_collection = current_app.db["topics"]

    user_email = get_jwt_identity()
    user = get_user_by_email(user_email, current_app.db["users"])

    if not user:
        return jsonify({"error": "User not authenticated"}), 401

    user_notes = notes_collection.find({"userId": user["sid"]}).sort("createdAt", -1)

    # Create a dictionary to map videoId to notes
    video_notes_map = {}
    for note in user_notes:
        if note["videoId"] not in video_notes_map:
            video_notes_map[note["videoId"]] = []
        video_notes_map[note["videoId"]].append({
            "notes": note["notes"],
            "createdAt": note["timestamp"],
        })

    # Fetch user topics and associated videos
    user_topics = topics_collection.find({"userId": user["sid"]})
    user_topics_list = []

    for topic in user_topics:
        video = videos_collection.find_one({"videoId": topic["videoId"]})
        video_detail = {
            "videoId": video["videoId"],
            "description": video["description"],
            "addedAt": topic["addedAt"],
            "notes": video_notes_map.get(video["videoId"], [])
        }

        # Check if the topic already exists in the user_topics_list
        existing_topic = next((t for t in user_topics_list if t["topic"]["id"] == topic["topics"]["id"]), None)
        
        if existing_topic:
            existing_topic["videos"].append(video_detail)
        else:
            user_topics_list.append({
                "topic": {
                    "category": topic["topics"]["category"],
                    "id": topic["topics"]["id"],
                },
                "videos": [video_detail]
            })

    return jsonify({'watch_history': user_topics_list}), 200

@bp.route('/watch-history')
def history():
    if request.method == 'GET':
        pass
    if request.method == 'POST':
        db_videos = current_app.db["videos"]
            
@bp.route('/update_watch_history', methods=['POST'])
@jwt_required
def update_history():
    db_videos = current_app.db["videos"]
    db_watch_history = current_app.db["watch_history"]

    video_id = request.json.get("video_id")
    if not video_id:
        return jsonify({"error": "Video ID is required"}), 400
    
    timestamp = request.json.get("timestamp", 0)

    user = request.headers.get("access_token")
    if not user:
        return jsonify({"error": "User is required"}), 400

    video = db_videos.find_one({"videoId": video_id})
    if not video:
        return jsonify({"error": "Video not found"}), 404
    
    watch_history = db_watch_history.find_one({"videoId": video_id, "user": user})
    if watch_history:
        db_watch_history.update_one({"_id": watch_history["_id"]}, {"$set": {"timestamp": timestamp}})
    else:
        db_watch_history.insert_one({"videoId": video_id, "user": user, "timestamp": timestamp})

    return jsonify({"message": "Video watched successfully"}), 200