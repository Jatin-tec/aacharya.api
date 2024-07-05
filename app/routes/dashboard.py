from flask import Blueprint, current_app, jsonify, request
from bson.objectid import ObjectId
from ..services.chat_service import huggingface_ef
from ..services.auth_service import get_user_by_email
from flask_jwt_extended import jwt_required, get_jwt_identity


bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/', methods=['GET', 'POST'], endpoint='profile_view')
@jwt_required( )
def profile_view():
    try:
        # Establish a connection to the users collection
        notes = current_app.db["notes"]
        watch_history = current_app.db["watch_history"]
        videos = current_app.db["videos"]
        topics = current_app.db["topics"]

        user =  get_jwt_identity()
        user = get_user_by_email(user, current_app.db["users"])

        if not user:
            return jsonify({"error": "User not authenticated"}), 401
        
        notes = notes.find({"userId": user["sid"]}).sort("createdAt", -1)

        notes_list = []
        for note in notes:
            notes_list.append({
                "videoId": note["videoId"],
                "userId": note["userId"],
                "notes": note["notes"],
                "createdAt": note["timestamp"],
            })

        watch_history = watch_history.find({"user.sid": user["sid"]}).sort("timestamp", -1)
        vectorstore = current_app.vectorstore
        collection = vectorstore.get_or_create_collection(name="yt_transcripts")
        
        user_topics = topics.find({"userId": user["sid"]})

        user_topics_list = []
        for topic in user_topics:
            video = videos.find_one({"videoId": topic["videoId"]})
            user_topics_list.append({
                "topic": {
                    "category": topic["topics"]["category"],
                    "id": topic["topics"]["id"],
                },
                "video": {
                    "videoId": video["videoId"],
                    "description": video["description"],
                },
            })


        # watch_history_list = []
        # for video in watch_history:
        #     video = videos.find_one({"videoId": video["videoId"]})
        #     similar_videos = collection.query(query_embeddings=huggingface_ef(video["script"]), include=[ "documents" ])
        #     watch_history_list.append({
        #         "video": {
        #             "videoId": video["videoId"],
        #             "description": video["description"],
        #         },
        #         # "timestamp": video["timestamp"],
        #         "similar_videos": similar_videos
        #     })

        return jsonify({"notes": notes_list, "watchHistory": user_topics_list}), 200

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