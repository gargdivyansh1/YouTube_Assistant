from fastapi import FastAPI
from pydantic import BaseModel 
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from backend.main import get_transcript, merge_and_split_segments, get_session_history
from backend.main import chain_with_memory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
import re

INDEX_NAME = "youtube-assistant"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class ChatRequest(BaseModel):
    session_id: str
    question: str
    video_id: str  

class ChatResponse(BaseModel):
    answer: str

retriever_cache = {}
transcript_cache = {}  # cache full transcript per video

# detect broad queries like "explain the video"
def is_broad_query(question: str) -> bool:
    broad_patterns = [
        r"explain (the )?video",
        r"summarize",
        r"what('?s| is) (this|the) video about",
        r"give (me )?(an )?overview",
        r"tell me about (this|the) video"
    ]
    return any(re.search(p, question.lower()) for p in broad_patterns)

# a route for keeping the backend active on free service on render
@app.head("/uptime")
def uptime():
    return {"status": "alive"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):

    video_id = request.video_id
    session_id = request.session_id
    question = request.question

    # Build retriever & cache transcript if not already
    if video_id not in retriever_cache:
        print(f'Building retriever for new video: {video_id}')

        video_url = f"https://www.youtube.com/watch?v={video_id}"
        transcript = get_transcript(video_id, video_url)
        chunks = merge_and_split_segments(transcript, target_chunk_size=400)

        if not chunks:
            return ChatResponse(answer="No transcript available for this video.")
        
        # Cache the full transcript text (joined chunks)
        transcript_cache[video_id] = " ".join(chunk["text"] for chunk in chunks)

        # Init Pinecone + embeddings
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        if INDEX_NAME not in pc.list_indexes().names():
            pc.create_index(
                name=INDEX_NAME,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )

        embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002", 
            api_key=os.getenv("OPENAI_API_KEY") #type:ignore
        )

        vectorstore = PineconeVectorStore.from_texts(
            texts=[chunk["text"] for chunk in chunks],
            embedding=embeddings,
            index_name=INDEX_NAME,
            namespace=video_id,  # different namespace for each video
            metadatas=[{"start": chunk["start"], "duration": chunk["duration"]} for chunk in chunks],
        )

        retriever_cache[video_id] = vectorstore.as_retriever(
            search_type='similarity',
            search_kwargs={'k': 6}, 
            namespace=video_id
        )
    else:
        print(f"Using cached retriever for video: {video_id}")

    retriever = retriever_cache[video_id]

    # Use full transcript for broad queries
    if is_broad_query(question):
        print(f"[Video: {video_id}] Broad query detected → using full transcript")
        context = transcript_cache.get(video_id, "")
    else:
        context = retriever.invoke(question)

    response = chain_with_memory.with_config(
        configurable={"session_id": request.session_id}
    ).invoke({
        'question': question,
        'context': context,
        'history': get_session_history(session_id).messages
    })

    print(f"[Video: {video_id}] Q: {question} → A: {response.content}")

    return ChatResponse(answer=response.content)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)