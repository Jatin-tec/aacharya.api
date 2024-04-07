from flask import Flask, request, jsonify, render_template, Blueprint, redirect, url_for, session
from flask import current_app as app
from googleapiclient.discovery import build
from ..services.auth_service import login_required

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
@login_required
def main():
    search_query = request.args.get('q')
    if not search_query:  
        return render_template('home.html')
    else:  
        try:
            api_key = app.config.get("YOUTUBE_API")
            youtube = build("youtube", "v3", developerKey=api_key)

            
            response = youtube.search().list(
                q=search_query,
                part="id,snippet",
                maxResults=6  
            )
            response = response.execute()

            # Process the response
            results = []
            for item in response.get("items", []):
                video_id = item["id"].get("videoId")  
                if video_id:
                    video_info = {
                        "title": item["snippet"]["title"],
                        "video_id": video_id,
                        "description": item["snippet"]["description"]
                    }
                    results.append(video_info)

            return render_template('home.html', results=results)

        except Exception as e:
            print("An error occurred:", str(e))
            return jsonify([])  
