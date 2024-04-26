from flask import Blueprint, render_template, request, jsonify
from ..services.llm_service import wrapper
from ..services.chat_service import get_transcript, crop_transcript, huggingface_ef, document_exists
from ..services.auth_service import login_required, get_user_info
from flask import current_app
import uuid
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

@bp.route('/transcript')
# @login_required
def transcript():
    video_id = request.args.get('q')
    transcript = get_transcript(video_id)
    return jsonify(transcript)

@bp.route('/ask', methods=['POST'])
# @login_required
def ask():
    mongo = current_app.db["conversations"]
    
    data = request.json
    user_message = data['message']
    timestamp = data.get('timestamp', 0)  # Default to 0 if not provided

    video_id = request.args.get('q')
    print(user_message, timestamp, video_id)

    transcript = get_transcript(video_id)



    summarize = request.args.get('summarize', False)

    # Crop the transcript up to the provided timestamp
    cropped_transcript = crop_transcript(transcript, timestamp)

    print(cropped_transcript, 'cropped_transcript')

    # return jsonify({'response': cropped_transcript})
    
    vectorstore = current_app.vectorstore
    response = wrapper.generate_response(user_message, context=cropped_transcript, vectorstore=vectorstore)
    
    if summarize:
        chat = current_app.db["chats"]
        conversation = chat.find_one({"videoId": video_id, "userId": get_user_info()["sub"]})
        
        questions = []
        if conversation:
            for q in conversation:
                text = q["questions"][0]["text"]
                questions.append(text)
        response = wrapper.generate_response(user_message, context=transcript, vectorstore=vectorstore, summary=True, questions=questions)
    
    response_msg = ""
    for r in response:
        print(r)
        if r["choices"][0]["delta"] == {}:
            break
        msg = r["choices"][0]["delta"]["content"]
        response_msg += msg

    wrapper.history.append({
        "role": "user", 
        "content": user_message
    })

    print(response_msg, 'response_msg')

    # user_id = get_user_info()["sub"]

    # # Store system response
    # mongo.insert_one({   
    #     "videoId": video_id,
    #     "userId": user_id,
    #     "transcript": transcript,
    #     "timestamp": datetime.datetime.now(),
    #     "questions": [
    #         {
    #         "text": user_message,
    #         "response": response_msg
    #         }
    #     ]
    # })

    # if summarize:
    #     notes = current_app.db["notes"]
    #     notes.insert_one({
    #         "videoId": video_id,
    #         "userId": user_id,
    #         "notes": response_msg
    #     })

    return jsonify({'response': response_msg})
