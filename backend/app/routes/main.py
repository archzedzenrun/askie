from flask import Blueprint, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from app.helpers import flatten_transcript, chunk_transcript, generate_summary
from app.db import get_connection, store_embeddings, store_messages


ytt_api = YouTubeTranscriptApi()
main = Blueprint('main', __name__)

# @main.route("/api/chunk", methods=["POST"])
# def chunk():
#     data = request.get_json()
#     video_id = data["video_id"]
#     transcript = ytt_api.fetch(video_id).to_raw_data()
#     flat_transcript = flatten_transcript(transcript)
#     chunked_transcript = chunk_transcript(flat_transcript)
#     print(chunked_transcript)
#     return jsonify({"chunks": chunked_transcript}), 200

@main.route("/api/videos", methods=["GET"])
def videos():
    response = { "message": "", "data": [] }
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM videos")
                rows = cursor.fetchall()
                for row in rows:
                    response["data"].append({
                        "id": str(row[0]),
                        "video_id": row[1],
                        "title": row[2],
                        "description": row[3],
                        "summary": row[4],
                        "date_created": row[5].strftime('%d-%m-%Y %H:%M:%S')
                    })
                response["message"] = f"""{len(response["data"])} {"Transcript" if len(response["data"]) == 1 else "Transcripts"} retrieved successfully"""
                return jsonify(response), 200
    except Exception as e:
        response["message"] = "Error retrieving transcripts"
        return jsonify(response), 500

@main.route("/api/embed_transcript", methods=["POST"])
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
                
                flat_transcript = flatten_transcript(transcript)
                summary = generate_summary(flat_transcript)
                chunked_transcript = chunk_transcript(flat_transcript)
                print(summary)
                cursor.execute(
                    "INSERT INTO videos (video_id, title, description, summary) VALUES (%s, %s, %s, %s) RETURNING *",
                    (video_id, data["title"], data.get("description", ""), summary)
                )
                video_row = cursor.fetchone()
                print("VIDEO ROW:", video_row)
                video_db_id = video_row[0]

                response = {
                        "id": str(video_row[0]),
                        "video_id": video_row[1],
                        "title": video_row[2],
                        "description": video_row[3],
                        "summary": video_row[4],
                        "date_created": video_row[5].strftime('%d-%m-%Y %H:%M:%S')
                }
                print(response)
                store_embeddings(chunked_transcript, video_db_id, cursor)
                conn.commit()

        return jsonify({"message": "Embeddings generated successfully!", "video_data": response}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/api/query", methods=["POST"])
def query():
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "No query provided"}), 400
    if "video_id" not in data:
        return jsonify({"error": "No video id provided"}), 400
    
    video_id = data["video_id"]
    query = data["query"]
    
    try:
        answer = store_messages(query, video_id)
        return jsonify(answer), 201
        with get_connection() as conn:
            with conn.cursor() as cursor:
               
                results = perform_vector_search(q, cursor, video_id)
                print(results)
                return results, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@main.route("/api/messages/<video_id>", methods=["GET"])
def get_messages(video_id):
    print(video_id)
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        m.id,
                        m.role,
                        m.message,
                        m.created_at,
                        v.video_id
                    FROM messages AS m
                    JOIN videos AS v ON m.video_id = v.id
                    WHERE v.video_id = %s
                    ORDER BY m.created_at ASC;
                    """,
                    (video_id,)
                )
                rows = cursor.fetchall()

                messages = [
                    {
                        "id": str(row[0]),
                        "role": row[1],
                        "content": row[2],
                        "created_at": row[3].strftime('%d-%m-%Y %H:%M:%S'),
                        "video_id": row[4]
                    }
                    for row in rows
                ]
                return jsonify(messages), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
