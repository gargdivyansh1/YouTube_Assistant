# YouTube Assistant

**YouTube Assistant** brings advanced, AI-powered conversational understanding to every YouTube video through a seamless browser extension and a sophisticated, scalable backend. It’s more than just a Q&A bot: it’s an extensible, distributed knowledge infrastructure for the world’s video content.

---

## Table of Contents

- [Overview](#overview)
- [Extraordinary Tech: Planet-Scale Vector Caching](#extraordinary-tech-planet-scale-vector-caching)
- [Features](#features)
- [Architecture](#architecture)
- [Deep Technical Details](#deep-technical-details)
  - [Backend Walkthrough](#backend-walkthrough)
  - [Chrome Extension Walkthrough](#chrome-extension-walkthrough)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)

---

## Overview

YouTube Assistant enables users to ask questions about any YouTube video and get context-rich, intelligent answers—directly within the YouTube interface. Unlike simple AI overlays that just transcribe video or answer with general context, this assistant processes, stores, and retrieves its knowledge *for all users*, turning every video into a persistent, shareable knowledge object.

---

## Extraordinary Tech: Planet-Scale Vector Caching

> **🌍 Infinite Scalability & Shared Intelligence:**
>
> - YouTube Assistant employs a state-of-the-art strategy for transcript storage and knowledge retrieval: **transcripts and semantic embeddings for each video are computed ONCE, then cached as vectors in a global database (Pinecone).**
> - **No matter how many users (from one to a billion) ask questions about a given video, the backend only needs to transcribe, embed, and store the content a single time.** All subsequent queries, worldwide, access instant context and answers—no duplicated costs, no redundant delay.
> - **Ultra-efficient:** Massive computational and cost savings for viral, trending, or evergreen videos.
> - **Global Knowledge Graph:** As more users interact, the quality and richness of responses grow stronger, making this assistant a planetary-scale reference system for video content.
> - **Collaboration Ready:** Moderation, annotation, or advanced features can be layered atop this shared knowledge vector store—any improvement is instantly available to all.

---

## Features

- **Ask any question about any YouTube video**—from summaries and deep explanations to very specific queries.
- **Automatic transcript retrieval**—uses official captions if available; otherwise, downloads audio and transcribes using Whisper ASR.
- **Semantic chunking and vector memory:** Chunks and embeds video knowledge using OpenAI & Pinecone for high-relevance search.
- **Handles broad and focused queries:** Special-case handling for summary/overview questions versus targeted lookups.
- **Persistent context:** Chat history and context are stored for smooth, multi-turn, in-depth conversations.
- **Voice input & output:** Natural language interface with voice recognition and synthesized answers.
- **Zero friction:** Plug in the Chrome extension and backend, and every YouTube video becomes a live knowledge source.
- **Designed for massive scale:** Any number of users, any volume of repeated questions, one global vector cache per video.

---

## Architecture

```
YouTube_Assistant/
├── backend/
│   ├── main.py                 # Transcript fetch, ASR fallback, chunking, vector embedding, prompt logic
│   ├── index.py                # FastAPI server, chat API, caching, orchestrating vector store
│   ├── requirements.txt        # All backend dependencies (LLM, ASR, vector DB, server)
│   ├── __init__.py
├── chrome_extension/
│   ├── content.js              # Injected interface/UI logic, message passing, voice
│   ├── background.js           # Backend API relay, message handler
│   ├── manifest.json           # Chrome extension config
├── .env.sample                 # Sample .env for backend API/secret keys
├── .gitignore
└── README.md
```

---

## Deep Technical Details

### Backend Walkthrough

- **Transcript Acquisition Workflow**  
  - For any given video ID:  
    - **Attempt to fetch captions with `youtube-transcript-api`.**  
    - If *not available*, **download the audio via `yt-dlp`**, then transcribe it using `faster-whisper` (an efficient automatic speech recognition model).
    - **Audio is auto-chunked for large files** to avoid memory/computational bottlenecks.

- **Semantic Chunking & Embedding**  
  - Transcripts are split into overlapping, contextually-aware chunks with `RecursiveCharacterTextSplitter` from LangChain.
  - Each chunk is embedded via `OpenAIEmbeddings` and stored in Pinecone under a namespace unique to the video ID.

- **Planet-Scale Vector Store**
  - On the **first request for a video**, transcript chunks are processed and embedded; on **all future requests for the same video**, the cached vector store is used instantly—**no matter the user**.
  - *This pattern means a viral or trending video’s transcript is only computed once and forever globally available.*

- **Intelligent Retrieval**
  - For “broad” queries (e.g., _summarize, tell me about_), the whole transcript is used for context; for specific queries, a vector similarity search efficiently retrieves the most relevant parts.
  - Uses LangChain’s powerful chain orchestration (`chain_with_memory`) for reasoning over context and maintaining session-specific chat history in memory.

- **API & Extensibility**
  - Exposes a FastAPI `/chat` endpoint; all extension queries go here.
  - Cross-Origin Resource Sharing (CORS) is configured for seamless extension-backend communication.
  - Backend is easily extensible for more features (moderation, advanced analytics, etc.).

- **All dependencies** are specified in `backend/requirements.txt`—includes FastAPI, LangChain, Pinecone, Whisper, OpenAI, audio processors, and environment managers.

---

### Chrome Extension Walkthrough

- **UI Overlay:**  
  - A draggable, minimizable, polished UI injected into every YouTube watch page.
  - Rich textarea with live character count, ‘Ask’ and 'Speak' controls, answer area with formatting and "thinking" animations, and voice toggle options.
- **Voice Recognition:**  
  - Uses Web Speech API (works in Chrome/Edge) for hands-free, conversational queries.
- **Voice Output:**  
  - Synthesizes answer audio for accessibility and richer experience.
- **Video Context Extraction:**  
  - Automatically detects the YouTube video ID, handles `/watch`, `/shorts`, and `/embed` URLs.
- **Background API Handler:**  
  - All queries are sent as messages to a lightweight background script, which handles POST requests to the FastAPI backend and returns answers.
- **Flexible Permissions:**  
  - Manifest grants only necessary access, scoped to YouTube URLs and backend service endpoint.
- **No data ever stored on the client:**  
  - All knowledge persists in the backend or vector store; user privacy is respected and the knowledgebase remains consistent and shareable.

---

## Setup & Installation

### Backend

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gargdivyansh1/YouTube_Assistant.git
   cd YouTube_Assistant/backend
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Copy and configure environment:**
   ```bash
   cp ../.env.sample ../.env
   ```
   - Edit `.env` and set your `OPENAI_API_KEY`, `PINECONE_API_KEY`, and any other required subscriptions/keys.
4. **Start the backend server:**
   ```bash
   uvicorn index:app --reload
   # or python index.py for standalone run
   ```

### Chrome Extension

1. **Open Chrome and go to `chrome://extensions/`.**
2. **Enable "Developer Mode".**
3. **Click “Load Unpacked” and choose the `chrome_extension/` folder.**
4. **Navigate to any YouTube video. The floating assistant will appear.**

---

## Configuration

- Edit `.env` at the project root to add your API keys and service endpoints.
- Pinecone and OpenAI credits/subscriptions are required for vector storage and LLM-based answering.
- The backend's `/chat` endpoint URL must match what’s set in the extension.

---

## Contributing

- Fork the repo and create a new branch for your changes.
- Open an issue or discussion for major suggestions.
- Be clear about test cases and improvement rationale.
- Pull requests are welcome!

---

## Acknowledgements

- [LangChain](https://github.com/langchain-ai/langchain)
- [OpenAI](https://openai.com/)
- [Pinecone](https://www.pinecone.io/)
- [Whisper ASR](https://github.com/openai/whisper)
- [FastAPI](https://fastapi.tiangolo.com/)
- Special thanks to the open-source community for tools that make this possible.

---
