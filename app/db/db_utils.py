import psycopg2
from app.config import Config
from app.helpers.transcript_utils import generate_embedding

def get_connection():
    return psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
    )

def store_embeddings(transcript, video_db_id, cursor):
    # try:
    #     conn = get_connection()
    #     cursor = conn.cursor()
    for snippet in transcript:
        embedding = generate_embedding(snippet)
        cursor.execute(
            "INSERT INTO transcript_embeddings (video_id, transcript, embedding) VALUES (%s, %s, %s)",
            (video_db_id, snippet, embedding)
        )
        print(f"Stored embedding for: {snippet[:50]}...")

        # conn.commit()
    print("All embeddings stored successfully!")

    # except Exception as e:
    #     print("Error generating embeddings:", e)

    # finally:
    #     cursor.close()
    #     conn.close()

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
