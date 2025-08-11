from .db_utils import get_connection

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id SERIAL PRIMARY KEY,
                video_id TEXT UNIQUE NOT NULL,
                title TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS "transcript_embeddings" (
                id SERIAL PRIMARY KEY,
                video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
                transcript TEXT NOT NULL,
                embedding vector(1536)
            );
        """)
        conn.commit()
        print("Database setup complete!")
    except Exception as e:
        print("Error during setup:", e)
    finally:
        cur.close()
        conn.close()
        print("Database connection closed.")
