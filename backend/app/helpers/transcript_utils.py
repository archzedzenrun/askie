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
    MAX_TOKENS = 500  # per chunk, adjust based on your embedding model
    OVERLAP = 50      # token overlap for better context preservation

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

chunked = chunk_transcript("""[Music] your brain is the most powerful weapon in the world once you put away your phones and your computers and all that we have nowadays that's great we're up
-to-date you know you but your brain is the only thing you have when you're going through depression when you're going through hard times you're going through death real life you can't Google that man you're alone you're alone you may have a shrink you're going to you may have a best friend you going to but there's 24 hours in the day where you're alone in this brain and your brain is talking to you in all kind of ways and it wants to control you and pull you in these different pockets if you can't control your own brain and your brain controls you you're you got to tell your brain where you want to go and how you want to go and how you want to get there you got to control it if not it's over but existed for me was okay man how am I gonna make this work and all I knew back then was hard work the only way anything gets accomplished that's all I heard back in those days you got to work hard you got to work hard I'm not getting how did I can't get this paragraph I can't remember what this paragraph to pass this test to get the military breathe again I'm still not getting it read again but it's not getting it write it out and now I started learning okay well I can't I gotta write out everything I do and then write it out again and write it out again and guess what happened I got it I got it I can't swim I'm negative buoyant go back again I can't swim go back again go back again go back again I got it I realize if I keep going back and going back and going back until this just becomes your mind was safe okay we're gonna figure it out because he is not going to stop it's like I'm gonna try one more time no I'm gonna it's just like long clock goes off Boop we're going back I can't read right we're going back I gave myself no way out and my mind realized that they said okay we're gonna adapt and overcome now like a lot of people say trying hard they your mind knows man it knows this guy's bull guys lying there's no truth behind it when I was a Navy SEAL training people oh how are you there for 18 months the program is always six months long you were in three hell weeks in one year no one's ever done that how did you do that I talked about the new norm when I lived in the $7 a month place and I was growing up for a short period of time I loved it I don't know you know any different that was my norm once we move down that place we moved to $236 month place I was like I never want to go back to that little pieces but if you go back to that seven dollar month place and you realize this is where I live that's all I got your mind says Roger that this is home so when I was going to Navy SEAL training for 18 months and going back through all the hard part's over and over again I told myself after the first time I knew this could be a long journey there my body was breaking down it was it was just how it was going on I see know what this is my new normal so my mind said is that going to work like you go to work you put your suit I on I'm going to suffering every day every day suffering being broken duct taping my feet up stress fracture shin splints being broken this is my new norm and your mind says if we're not broken just say normal we got to be broken so then your mind starts to get tougher and tougher and more cast people huh how did you run on broken feet broken broken shins my mind knew this is how we operate we're a Navy SEAL training this is what we are I health and that became my new norm I gave myself no way out there was nothing outside these walls of hell nothing I became I love God but for a short period of time I became the devil because that was hell I became I became the boss the owner the CEO of Navy SEAL training that was my mindset and that's how you get through things you put yourself you immerse yourself wherever it is you become that you become that and give yourself nowhere yeah when I was tours in 97 pounds and I was fat as hell trying to be a Navy SEAL the scariest thing in the world to me even to this day was that that could have been the rest of my life I thought then I was trying hard that's the scariest thing in the world I thought then two or 97-pound working for Ecolab's spraying for cockroaches making $1,000 a month I thought that was me at my 100% potential come to find out a few years later I wasn't even near that 106 pounds less graduating Navy SEAL training we don't do all these other things looking back on that that was me trying hard that's why people got understand what is in us we have no idea until we start trying hard and I mean really trying hard where you're obsessed with hey this is my new norm my new norm is that wow this isn't always fun it's not always meant to be fun and that's when you know you're trying hard people hear my story and think this guy's sadistic I realize how the how the brain works I figured out how the brain works I'm a scared kid and that's what gives me so much power I had no foundation and I built this off of just researching the mind the feeling you get is basically invincibility you realize that you can't do it all the time when you need to do it I know I can go to a place that I can live in and when you know that you can run on broken legs and you can do certain things that a lot of people can do but they're not willing to do this power this sympathetic nervous system of fight or flight and you're fighting it gives you this charge of energy over when you're sitting there at 3:30 4:00 o'clock in the morning and you're duct taping your feet up because they're broken and you're doing it by yourself and you're going to do arguably one of the hardest training in the world and these guys most of them are healthy and you're going through it broken and you already at a disadvantage but you're still there you can feed into that and tap into that for a lot of power but if you look at it while I'm broken man like I'm not gonna make it if you look at it as man I'm broken and I'm still here and I'm fighting and I'm gonna find a way to get through this because I have no other place to go it gives you a lot of power when things start to suck really really bad my brain and a lot of people's brain DUP they don't go to your dad beating you up your brain says win it right here this is miserable so anger goes away a lot of times when you're suffering because your brain that says we got a run we got to go so that anger is not popping up saying oh I'm gonna show them I want to show those people no there has to be a much deeper if I say deeper it has to be down to mineral mineral soil it has to be down to that nice mineral soil where nothing can burn you can't burn dirt so it has to be down that low that literally is submenu that's at the core your soul and but you but you don't find it unless you spend a lot of time with what you want to be in life you I can't give that to you right you can't give it to somebody when when you find your true passion in life and my passion for me when like I want to be now given my Navy SEALs I mean roundish I want to serve my country I cared about I want to be someone that I'm proud of I want to look at myself in American I was so disappointed that accountability man I talked about I was so disappointed in what I saw every day I want everybody to love David Goggins and a lot of people did I didn't love myself but I knew a lot of us want to find peace first so gonna say man you always talk about this suffering and pain --is-- I'm at peace right now because I'm going to do that you don't find peace first if you do Merry Christmas more power to you more power to you I found peace on the opposite end of finding myself and no one really finds himself without going through trials tribulations suffering accountability and 
accountability is suffering being accountable every day for doing right for yourself for the people next to you it's miserable it's hard so you know even the sma
llest details you""")

# print(len(chunked))
# print(chunked)