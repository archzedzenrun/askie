from app.config import Config
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings

def flatten_transcript(segments):
    return " ".join(
        seg["text"].replace("\n", " ").strip()
        for seg in segments
    )

def chunk_transcript(transcript):
    text_splitter = SemanticChunker(
        OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY),
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=50.0,
        min_chunk_size=200,
    )
    
    chunk_documents = text_splitter.create_documents([transcript])
    chunks = [document.page_content for document in chunk_documents]
    return chunks

def generate_embedding(query):
    response = Config.OPENAI_CLIENT.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
    return response.data[0].embedding

def generate_response(question, video_id):
    from app.db.db_utils import perform_vector_search
    original_question = question
    embedding = generate_embedding(question)
    relevant_answers = perform_vector_search(embedding, video_id, limit=5)
    print(relevant_answers)
    if not relevant_answers:
        return "I couldn't find any relevant answers. Please ask another question."

    context = "\n".join([
        f"- {result[0]} (Similarity: {result[1]:.2f})"
        for result in relevant_answers
    ])

    prompt = f"""You are an assistant that answers questions based on the transcript of a YouTube video.

    Use the following transcript excerpts to answer the user's question. 
    If the excerpts don't contain enough relevant information, say that you can't find the answer in the transcript.

    Transcript excerpts:
    {context}

    User's Question: {original_question}

    Answer clearly, concisely, and based only on the provided transcript content. Do not use statements like "Based on the transcript". If you add extra knowledge, make it clear that it's outside the transcript."""

    response = Config.OPENAI_CLIENT.responses.create(
        model="gpt-4",
        input=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
    )
    print(response.output_text)
    return response.output_text

def generate_summary(transcript):
    prompt = f"""You are a helpful assistant. Summarize the following transcript of a video. 
    
    Provide your response in the following format:

    - Topic: 1-2 sentence summary of the main subject
    - Key Points: 3–5 bullet points with the most important details
    - Overall Takeaway: 1–3 sentences

    Transcript:
    {transcript}
    """

    response = Config.OPENAI_CLIENT.responses.create(
        model="gpt-4",
        input=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
    )
    print(response.output_text)
    return response.output_text