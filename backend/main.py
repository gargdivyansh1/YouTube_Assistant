from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import yt_dlp
from faster_whisper import WhisperModel
import os
from pydub import AudioSegment
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
ytt_api = YouTubeTranscriptApi()

def get_audio_from_youtube(url, output_path="audio.mp3"):
    ydl_opts = {"format": "bestaudio/best", "outtmpl": output_path, "postprocessors": []}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

def split_audio(audio_path, chunk_length_ms=300000):
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i+chunk_length_ms]
        chunk_path = f"chunk_{i//chunk_length_ms}.mp3"
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)
    return chunks

def get_transcript(video_id, video_url):
    try:
        fetched_transcript = ytt_api.fetch(
            video_id,
            languages=["en", "hi", "es", "fr", "de", "ru", "pt", "ja", "ko", "zh-Hans", "ar"]
        )
        transcript = [
            {"text": chunk.text, "start": chunk.start, "duration": chunk.duration}
            for chunk in fetched_transcript
        ]
        return transcript
    except TranscriptsDisabled:
        print("No captions available, falling back to ASR...")
        audio_file = get_audio_from_youtube(video_url)
        audio_size = os.path.getsize(audio_file) / (1024 * 1024)
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        
        transcript_segments = []
        current_time = 0
        
        if audio_size < 25:
            segments, _ = model.transcribe(audio_file)
            for segment in segments:
                transcript_segments.append({
                    "text": segment.text,
                    "start": segment.start,
                    "duration": segment.end - segment.start
                })
        else:
            chunks = split_audio(audio_file)
            for chunk in chunks:
                segments, _ = model.transcribe(chunk)
                for segment in segments:
                    transcript_segments.append({
                        "text": segment.text,
                        "start": current_time + segment.start,
                        "duration": segment.end - segment.start
                    })
                current_time += 300  
                os.remove(chunk)
        
        return transcript_segments

def merge_and_split_segments(segments, target_chunk_size=250, chunk_overlap=50):
    if not segments or not isinstance(segments, list):
        return []
    
    if not all(isinstance(seg, dict) and "start" in seg and "text" in seg for seg in segments):
        return []
    
    segments = sorted(segments, key=lambda x: x["start"])
    merged, current = [], None

    for seg in segments:
        seg_start, seg_end = seg["start"], seg["start"] + seg["duration"]
        if current is None:
            current = {"text": seg["text"], "start": seg_start, "end": seg_end}
        else:
            if seg_start <= current["end"]:
                current["text"] += " " + seg["text"]
                current["end"] = max(current["end"], seg_end)
            else:
                merged.append({
                    "text": current["text"].strip(),
                    "start": current["start"],
                    "duration": current["end"] - current["start"]
                })
                current = {"text": seg["text"], "start": seg_start, "end": seg_end}
    if current:
        merged.append({
            "text": current["text"].strip(),
            "start": current["start"],
            "duration": current["end"] - current["start"]
        })

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=target_chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "।", "?", "!", " ", ""]
    )
    final_chunks = []
    for chunk in merged:
        text, start, duration = chunk["text"], chunk["start"], chunk["duration"]
        split_texts = splitter.split_text(text)
        if len(split_texts) == 1:
            final_chunks.append(chunk)
        else:
            total_len = len(text)
            for part in split_texts:
                part_ratio = len(part) / total_len
                part_duration = duration * part_ratio
                final_chunks.append({"text": part.strip(), "start": start, "duration": part_duration})
                start += part_duration
    return final_chunks

prompt = ChatPromptTemplate.from_template("""
You are a helpful and intelligent AI assistant with both memory and access to retrieved knowledge. 
You are provided with the content of the video .. hence you have the access as you know the information.
Your goal is to provide accurate, thoughtful, and context-aware responses to the user. 
You can perform multiple types of tasks, such as answering questions, generating text, summarizing, 
explaining concepts, giving recommendations, and more.
If the query is for summarizing or explaing the song or any poetry then do explain deeply.

### Available Information
- **Conversation History:** {history}
- **Retrieved Context from Documents:** {context}

### Instructions
1. Use the **history** and **retrieved context** when relevant. 
2. If user asks beyond this info, rely on your reasoning and general knowledge. 
3. Provide structured, clear, and user-friendly answers.

### User Request
{question}

### Your Response
""")

chain = prompt | llm

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history"
)
