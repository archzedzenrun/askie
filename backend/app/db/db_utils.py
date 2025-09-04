import psycopg2
from app.config import Config
from app.helpers.transcript_utils import generate_embedding, generate_response

def get_connection():
    return psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
    )

def store_embeddings(transcript, video_db_id, cursor):
    for snippet in transcript:
        embedding = generate_embedding(snippet)
        cursor.execute(
            "INSERT INTO transcript_embeddings (video_id, transcript, embedding) VALUES (%s, %s, %s)",
            (video_db_id, snippet, embedding)
        )
        print(f"Stored embedding for: {snippet[:50]}...")
    print("All embeddings stored successfully!")

def perform_vector_search(embedding, video_id, limit=5):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        te.transcript, 
                        1 - (te.embedding <=> %s::vector) AS similarity
                    FROM transcript_embeddings AS te
                    JOIN videos AS v ON te.video_id = v.id
                    WHERE v.video_id = %s
                      AND 1 - (te.embedding <=> %s::vector) > 0.5
                    ORDER BY similarity DESC
                    LIMIT %s;
                    """,
                    (embedding, video_id, embedding, limit)
                )

                return cursor.fetchall()
    except Exception as e:
        print("Error performing vector search:", e)
        return []

def store_messages(query, video_id):
    result = { "user": [], "assistant": [] }
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM videos WHERE video_id = %s", (video_id,))
            video_db_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO messages (video_id, role, message)
                VALUES (%s, %s, %s)
                RETURNING id, video_id, role, message, created_at
                """,
                (video_db_id, "user", query)
            )

            user_row = cursor.fetchone()
            result["user"] = {
                    "id": str(user_row[0]),
                    "video_id": user_row[1],
                    "role": user_row[2],
                    "content": user_row[3],
                    "created_at": user_row[4].strftime('%d-%m-%Y %H:%M:%S')
            }

            response = generate_response(query, video_id)

            cursor.execute(
                """
                INSERT INTO messages (video_id, role, message)
                VALUES (%s, %s, %s)
                RETURNING id, video_id, role, message, created_at;
                """,
                (video_db_id, "assistant", response)
            )

            assistant_row = cursor.fetchone()
            result["assistant"] = {
                    "id": str(assistant_row[0]),
                    "video_id": assistant_row[1],
                    "role": assistant_row[2],
                    "content": assistant_row[3],
                    "created_at": assistant_row[4].strftime('%d-%m-%Y %H:%M:%S')
            }

        conn.commit()
        return result