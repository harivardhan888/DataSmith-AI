
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
from agent_core import Agent

app = FastAPI()

# Make paths absolute to fix deployment issues (CSS not loading)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(BASE_DIR, "temp_uploads")

# Mount static files (Frontend)
os.makedirs(UPLOAD_DIR, exist_ok=True)

agent = Agent()

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.post("/api/chat")
async def chat_endpoint(
    message: str = Form(""),
    file: UploadFile = File(None)
):
    try:
        file_path = None
        file_type = None

        if file:
            # save file locally
            ext = file.filename.split(".")[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_type = file.content_type
            if not file_type:
                # manual fallback
                if ext in ['jpg', 'jpeg', 'png']: file_type = 'image/jpeg'
                elif ext == 'pdf': file_type = 'application/pdf'
                elif ext in ['.wav', '.mp3']: file_type = 'audio/mpeg'

        input_text = message if message.strip() else None

        # Process with agent
        response = await agent.process_input(
            text_input=input_text,
            file_path=file_path,
            file_type=file_type
        )
        
        # TODO: clean up temp files later
        
        return JSONResponse(content=response)

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return JSONResponse(content={"status": "error", "output": str(e)}, status_code=500)

app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")
