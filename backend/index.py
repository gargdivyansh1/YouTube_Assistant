from fastapi import FastAPI
from pydantic import BaseModel 
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from main import get_transcript, merge_and_split_segments
from main import chain_with_memory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
import re

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
store = {}

i = 1

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):

    video_id = request.video_id
    session_id = request.session_id
    question = request.question

    if video_id not in retriever_cache:
        print(f'Building retriever for new video: {video_id}')

        video_url = f"https://www.youtube.com/watch?v={video_id}"
        transcript = get_transcript(video_id, video_url)
        print(transcript)
        chunks = merge_and_split_segments(transcript, target_chunk_size=400)

        if not chunks:
            return ChatResponse(answer= "No transcript available for this video.")
        
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        safe_id = re.sub(r'[^a-z0-9]', '-', video_id.lower())
        index_name = f"yt-abc{i+1}"

        if index_name not in pc.list_indexes().names():
            pc.create_index(
                name=index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )

        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=os.getenv("OPENAI_API_KEY")) #type:ignore

        vectorstore = PineconeVectorStore.from_texts(
            texts=[chunk["text"] for chunk in chunks],
            embedding=embeddings,
            index_name=index_name,
            metadatas=[{"start": chunk["start"], "duration": chunk["duration"]} for chunk in chunks],
        )

        retriever_cache[video_id] = vectorstore.as_retriever(search_type='similarity', search_kwargs={'k': 4})
    else:
        print(f"Using cached retriever for video: {video_id}")

    retriever = retriever_cache[video_id]

    response = chain_with_memory.with_config(
        configurable ={"session_id": request.session_id}
    ).invoke({
        'question': question,
        'context': retriever.invoke(question),
        'history': get_session_history(session_id).messages
    })

    print(f"[Video: {video_id}] Q: {question} → A: {response.content}")

    return ChatResponse(answer=response.content)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)