from flask import Blueprint, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from app.helpers import flatten_transcript, chunk_transcript, ask_transcript_question
from app.db import get_connection, store_embeddings


ytt_api = YouTubeTranscriptApi()
main = Blueprint('main', __name__)

@main.route("/embed_transcript", methods=["POST"])
def embed_transcript():
    data = request.get_json()
    if not data or "video_id" not in data or "title" not in data:
        return jsonify({"error": "Missing title or video id"}), 400
    
    video_id = data["video_id"]

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM videos WHERE video_id = %s", (video_id,))
                if cursor.fetchone():
                    return jsonify({"message": "Video already exists."}), 200
                
                transcript = ytt_api.fetch(video_id).to_raw_data()

                if not transcript:
                    return jsonify({"error": "No transcript found for the provided video id"}), 404
                
                cursor.execute(
                    "INSERT INTO videos (video_id, title, description) VALUES (%s, %s, %s) RETURNING id",
                    (video_id, data["title"], data.get("description", ""))
                )
                video_db_id = cursor.fetchone()[0]
    
                flat_transcript = flatten_transcript(transcript)
                chunked_transcript = chunk_transcript(flat_transcript)

                store_embeddings(chunked_transcript, video_db_id, cursor)
                conn.commit()

        return jsonify({"message": "Embeddings generated successfully!"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/search_transcript", methods=["POST"])
def search_transcript():
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "No query provided"}), 400
    if "video_id" not in data:
        return jsonify({"error": "No video id provided"}), 400
    
    video_id = data["video_id"]
    query = data["query"]

    try:
        answer = ask_transcript_question(query, video_id)
        return jsonify({"answer": answer}), 200
        with get_connection() as conn:
            with conn.cursor() as cursor:
               
                results = perform_vector_search(q, cursor, video_id)
                print(results)
                return results, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500