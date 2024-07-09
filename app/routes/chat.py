from flask import Blueprint, render_template, request, jsonify
from ..services.llm_service import wrapper
from ..services.chat_service import get_transcript, crop_transcript, huggingface_ef, document_exists, get_video_details
from ..services.auth_service import get_user_by_email
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from time import sleep
import uuid
import json
import datetime

bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route('/')
# @login_required
def sessions():
    # vectorstore = current_app.vectorstore

    video_id = request.args.get('q')
    # video_id = 'wjZofJX0v4M'

    if not video_id:
        return render_template('chat.html', videoURL=None)

    videoURL = f'https://www.youtube.com/embed/{video_id}' 
    # collection = vectorstore.get_or_create_collection(name="yt_transcripts")
    # exists = document_exists(collection, video_id)

    # if not exists:
    #     transcript = get_transcript(video_id)
    #     combined_transcript = []
    #     current_chunk = {"text": "", "start": 0, "duration": 0}
    #     chunk_duration = 120  # Duration in seconds for each chunk (5 minutes)

    #     for entry in transcript:
    #         # Skip non-dialogue entries
    #         if entry['text'] in ['[Music]', '[Applause]', '[Laughter]', '[Music Ends]']:
    #             continue

    #         if current_chunk["duration"] + entry['duration'] <= chunk_duration:
    #             # Append text to the current chunk if adding the current entry does not exceed chunk_duration
    #             current_chunk["text"] += (" " + entry['text']).strip()
    #             current_chunk["duration"] += entry['duration']
    #         else:
    #             # If adding the current entry exceeds chunk_duration, finalize the current chunk
    #             combined_transcript.append(current_chunk)
    #             current_chunk = {"text": entry['text'], "start": entry['start'], "duration": entry['duration']}

    #     # Add the last chunk if it's not empty
    #     if current_chunk["text"]:
    #         combined_transcript.append(current_chunk)


    #     documents = []
    #     metadatas = []
    #     ids = []
    #     embeds = []

    #     for entry in combined_transcript[:1]:
    #         try:
    #             if entry['text'] == '[Music]':
    #                 continue
    #             if entry['text'] == '[Applause]':
    #                 continue
    #             if entry['text'] == '[Laughter]':
    #                 continue
    #             if entry['text'] == '[Music Ends]':
    #                 continue
    #             if entry['text']:
    #                 embeds.append(huggingface_ef(entry['text']))
    #                 documents.append(entry['text'])
    #                 metadatas.append({"start": entry['start'], "duration": entry['duration'], "video_id": video_id})
    #                 ids.append(str(uuid.uuid4().hex))
    #         except Exception as e:
    #             print(f"Error processing transcript entry: {e}")
    #             continue
            
    #     print("Adding documents to collection...", ids, len(documents), len(embeds))
    #     collection.add(documents=documents, metadatas=metadatas, ids=ids, embeddings=embeds)
    return render_template('chat.html', videoURL=videoURL)

@bp.route('/transcript', methods=['GET', 'POST'])
@jwt_required(optional=False)
def transcript():
    video_id = request.args.get('q')

    mongo = current_app.db
    user_collection = current_app.db["users"]

    # vectorstore = current_app.vectorstore
    # collection = vectorstore.get_or_create_collection(name="videos")

    if not video_id:
        return jsonify({'response': 'video_id not provided'})
    
    current_user = get_jwt_identity()
    current_user = get_user_by_email(current_user, user_collection)

    if not current_user:
        return jsonify({'response': 'user not found'}, 401)
    
    transcript = get_transcript(video_id=video_id, mongo=mongo, userId=current_user["sid"])
    return jsonify(transcript)

@bp.route('/ask', methods=['POST'])
@jwt_required(optional=False)
def ask():
    mongo = current_app.db
    conversations_collection = mongo["conversations"]
    user_collection = mongo["users"]

    email = get_jwt_identity()
    user = get_user_by_email(email, user_collection)
    if not user:
        return jsonify({'response': 'user not authenticated'})
    
    data = request.json

    user_message = data['message']
    if not user_message:
        return jsonify({'response': 'message not provided'})

    timestamp = data.get('timestamp', 0)  # Default to 0 if not provided

    video_id = request.args.get('q')
    if not video_id:
        return jsonify({'response': 'video_id not provided'})
    
    transcript = get_transcript(video_id=video_id, mongo=mongo, userId=user["sid"])
    # Crop the transcript up to the provided timestamp
    cropped_transcript = crop_transcript(transcript, timestamp)

    response = wrapper.generate_response(user_message, context=cropped_transcript)
    wrapper.history.append({
        "role": "user", 
        "parts": response 
    })

    # Store system response
    conversations_collection.insert_one({   
        "videoId": video_id,
        "userId": user["sid"],
        "transcript": transcript,
        "timestamp": datetime.datetime.now(),
        "questions": [
            {
            "text": user_message,
            "response": response
            }
        ]
    })

    return jsonify({'response': response})

@bp.route('/summarize', methods=['POST'])
@jwt_required(optional=False)
def summarize():
    video_id = request.args.get('q')
    if not video_id:
        return jsonify({'response': 'video_id not provided'})
    
    user = get_user_by_email(get_jwt_identity(), current_app.db["users"])
    if not user:
        return jsonify({'response': 'user not authenticated'})
    
    conversation = request.json.get('conversation')
    if not conversation:
        conversation = []

    transcript = get_transcript(video_id=video_id, mongo=current_app.db, userId=user["sid"])

    script = ""
    for entry in transcript:
        script += entry['text'] + " "

    notes_collection = current_app.db["notes"]
    # generate smallers chunks of text
    chunk_size = 8000
    chunks = [script[i:i+chunk_size] for i in range(0, len(script), chunk_size)]

    print(f"Number of chunks: {len(chunks)}")

    response_msg = notes_collection.find_one({"videoId": video_id})
    if response_msg:
        response_msg = response_msg['notes']
    if not response_msg:
        # summarize each chunk
        response_msg = ""
        i = 1
        for chunk in chunks:
            if len(chunk) > 50:
                response = wrapper.generate_response(chunk, summary=True,  current=i, total=len(chunks), questions=conversation)
                response_msg += response
            i += 1
            print("Chunk processed")
            sleep(3)

        notes_collection.insert_one({
            "videoId": video_id,
            "userId": user["sid"],
            "notes": response_msg,
            "timestamp": datetime.datetime.now()
        })
    
    return jsonify({'response': response_msg})
