# DataSmith AI 

DataSmith is a lightweight, multimodal AI agent built to analyze text, images, audio, and video content instantly. It features a minimalist, "hacker-style" dark UI and is powered by Groq's Llama 3.3 models for extreme speed.

## Features

*   **Multimodal Chat**: Talk naturally with the AI.
*   **Vision Capabilities**: Upload images (screenshots, diagrams) and ask questions about them.
*   **YouTube Analysis**: Paste a YouTube link to get summaries, action items, or specific answers from the video.
*   **Document Processing**: Support for PDFs and text files (summarization, extraction).
*   **Smart Intent Detection**: Automatically figures out if you want a summary, code explanation, or just a chat.
*   **Demo Mode**: Built-in fallbacks ensure the demo never crashes, even if external APIs glitch.

## Tech Stack

*   **Frontend**: Vanilla HTML5, CSS3, JavaScript.
*   **Backend**: Python FastAPI.
*   **AI Engine**: Groq Cloud (Llama 3.3 70B Versatile, Llama Vision 3.2).
*   **Tools**: `youtube-transcript-api`, `pypdf`.



## Test Cases (Demo Flow)

Sample files for testing are located in the `input_samples/` folder. Use these files to verify the agent's capabilities.

### 1. General Chat
*   **Input**: "Who are you?"
*   **Expected**: "Hello! I am DataSmith AI. I can analyze texts, images, audio, and code..."

### 2. Code Explanation (Vision)
*   **Action**: Upload a screenshot of code (e.g., Python or C++ snippet).
*   **Input**: "Explain this code" or "What is the bug here?"
*   **Expected**: The Agent analyzes the image, extracts the code, and explains the logic or error.
*   *Fallback*: If the API fails, it will show a "[Demo Mode]" sample analysis of a Python function.

### 3. YouTube Video Summarization
*   **Input**: "Summarize this video: https://www.youtube.com/watch?v=x7X9w_GIm1s"
*   **Expected**: Fetches the transcript and provides a concise summary of "Python in 100 Seconds".
*   *Fallback*: If transcripts are disabled, it returns a "[Demo Limit]" sample summary about Generative AI.

### 4. Intent Mismatch (Reasoning)
*   **Action**: Upload a technical code screenshot.
*   **Input**: "Write a poem"
*   **Expected**: The Agent detects the mismatch between the serious file and the creative request. behavior.
    *   *Result*: "Do you want a poem ABOUT this code?" (Clarification) or a poem strictly about the code logic.

### 5. Document Analysis (PDF)
*   **Action**: Upload a simple text-based PDF (e.g., a resume or article).
*   **Input**: "Extract the main action items"
*   **Expected**: Bullet points listing key tasks or info found in the PDF.

## Architecture

```mermaid
graph TD
    User((User)) -->|Chat / Upload| UI[Frontend (HTML/JS)]
    UI -->|POST /api/chat| Server[FastAPI Server]
    
    subgraph Core Logic
    Server -->|Process Input| Agent[Agent Core]
    Agent -->|Identify Task| Intent[Intent Classifier]
    end
    
    subgraph Skills
    Agent -->|Extraction| Processor[File Processor]
    Processor -->|Image| Vision[Groq Vision Model]
    Processor -->|Video| YT[YouTube API]
    end
    
    subgraph Brain
    Intent -->|Query| LLM[Groq Llama 3]
    Agent -->|Generate| LLM
    end
    
    LLM -->|Response| Agent
    Agent -->|JSON| UI
```

## Project Structure

```
├── agent_core.py       # Main agent logic (Brain)
├── llm_service.py      # Groq API integration (Llama 3)
├── server.py           # FastAPI backend routes
├── requirements.txt    # Python dependencies
├── skills/
│   └── processor.py    # Vision, PDF, and YouTube tools
└── static/             # Frontend assets
    ├── index.html
    ├── style.css
    └── script.js
```

## Setup & Installation

1.  **Clone the repo**
    ```bash
    git clone https://github.com/yourusername/datasmith-ai.git
    cd datasmith-ai
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Variables**
    Create a `.env` file in the root directory:
    ```ini
    GROQ_API_KEY=gsk_your_key_here
    ```

4.  **Run the Server**
    ```bash
    python -m uvicorn server:app --reload --port 8000
    ```

5.  **Access the App**
    Open your browser and go to: `http://localhost:8000`

---
