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