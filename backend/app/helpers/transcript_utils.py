import tiktoken
from app.config import Config
from langchain_experimental.text_splitter import SemanticChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings

def count_tokens(text, model="text-embedding-3-small"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def flatten_transcript(segments):
    return " ".join(
        seg["text"].replace("\n", " ").strip()
        for seg in segments
    )

def chunk_transcript(transcript, model="text-embedding-3-small"):
    MAX_TOKENS = 500
    OVERLAP = 50

    # Step 1: Semantic chunking
    text_splitter = SemanticChunker(
        OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY),
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=30.0,
        min_chunk_size=200,
    )
    semantic_chunks = [doc.page_content for doc in text_splitter.create_documents([transcript])]

    # Step 2: Enforce token limit
    final_chunks = []
    for chunk in semantic_chunks:
        if count_tokens(chunk, model) > MAX_TOKENS:
            # Fall back to recursive character splitting while monitoring tokens
            char_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,  # large enough to keep context
                chunk_overlap=OVERLAP
            )
            sub_chunks = char_splitter.split_text(chunk)
            for sub_chunk in sub_chunks:
                if count_tokens(sub_chunk, model) <= MAX_TOKENS:
                    final_chunks.append(sub_chunk)
                else:
                    # Force further split if still too large
                    smaller_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=500,
                        chunk_overlap=OVERLAP
                    )
                    final_chunks.extend(smaller_splitter.split_text(sub_chunk))
        else:
            final_chunks.append(chunk)

    return final_chunks
    # word_count = len(transcript.split())

    # # Thresholds for different strategies
    # SHORT_THRESHOLD = 1000
    # MEDIUM_THRESHOLD = 5000

    # if word_count < SHORT_THRESHOLD:
    #     # No need to split very short transcripts
    #     return [transcript]

    # elif word_count < MEDIUM_THRESHOLD:
    #     # Use semantic chunking for mid-sized transcripts
    #     text_splitter = SemanticChunker(
    #         OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY),
    #         breakpoint_threshold_type="percentile",
    #         breakpoint_threshold_amount=30.0,
    #         min_chunk_size=200,
    #     )
    #     chunk_docs = text_splitter.create_documents([transcript])
    #     chunks = [doc.page_content for doc in chunk_docs]

    #     # Fallback if semantic chunking fails to split enough
    #     if len(chunks) <= 1:
    #         char_splitter = RecursiveCharacterTextSplitter(
    #             chunk_size=1000,
    #             chunk_overlap=200
    #         )
    #         chunks = char_splitter.split_text(transcript)

    #     return chunks

    # else:
    #     # For very large transcripts, avoid semantic chunking to save cost
    #     # Use aggressive character-based splitting
    #     char_splitter = RecursiveCharacterTextSplitter(
    #         chunk_size=1500,
    #         chunk_overlap=300
    #     )
    #     return char_splitter.split_text(transcript)

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

    Answer clearly, concisely, and based only on the provided transcript content. If you add extra knowledge, make it clear that it's outside the transcript."""

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
