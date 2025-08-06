from app.db import get_connection
from app.config import Config

def generate_embeddings(transcript, video_db_id, cursor):
    # try:
    #     conn = get_connection()
    #     cursor = conn.cursor()
    for snippet in transcript:
        # Create embedding with OpenAI
        response = Config.OPENAI_CLIENT.embeddings.create(
            model="text-embedding-3-small",
            input=snippet
        )
        embedding = response.data[0].embedding

        # Store in Postgres
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