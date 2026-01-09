import os
from pypdf import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi
from llm_service import LLMService

# global service (lazy init in functions if needed, or here)
llm_service = LLMService()

async def extract_content(file_path: str, file_type: str) -> str:
    # figure out what file this is and get text
    if not file_path: return ""

    # Image
    if 'image' in file_type or file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        return await _process_image(file_path)
        
    # PDF
    if 'pdf' in file_type or file_path.lower().endswith('.pdf'):
        return await _process_pdf(file_path)

    # Audio
    if 'audio' in file_type or file_path.lower().endswith(('.mp3', '.wav', '.m4a')):
        return llm_service.transcribe_audio(file_path)
        
    # Text
    if os.path.exists(file_path):
         try:
             with open(file_path, 'r', encoding='utf-8') as f:
                 return f.read()
         except:
             return "[Error processing text file]"

    return file_path


async def _process_image(file_path):
    # Use Llama Vision
    try:
        import base64
        
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        
        base64_image = encode_image(file_path)
        
        # quick service check
        from llm_service import LLMService 
        service = LLMService()
        
        if not service.client:
             return "[System: Groq API Key required for Image Analysis]"

        # model_id = "llama-3.2-11b-vision-preview" # this one is 11b
        model_id = "meta-llama/llama-4-scout-17b-16e-instruct" # trying scout
        
        try:
            chat_completion = service.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all text or describe this image."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                model=model_id,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            # Fallback for demo if API fails
            return (
                f"⚠️ **Vision API Error/Limit**: {str(e)}\n\n"
                "**[Demo Mode] Sample Analysis:**\n"
                "The image appears to be a code snippet written in Python. "
                "It defines a function `calculate_metrics` that takes `data` as input. "
                "Inside, there is a list comprehension filtering values > 0."
            )
        
    except Exception as e:
        return f"[System Error: {str(e)}]"

async def _process_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        
        if len(text) < 50:
             return "[PDF is empty or scanned image. OCR not enabled.]"
             
        return text
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"
        
async def extract_youtube_transcript(url: str) -> str:
    try:
        import re
        clean_url = url.strip("()<>.,;\"'")
        video_id = None
        
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', 
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})', 
            r'(?:embed\/)([0-9A-Za-z_-]{11})' 
        ]
        
        for pattern in patterns:
            match = re.search(pattern, clean_url)
            if match:
                video_id = match.group(1)
                break
        
        if not video_id:
             return f"Invalid YouTube URL: {clean_url}"

        # Standard processing
        try:
             transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
             full_text = " ".join([t['text'] for t in transcript_list])
             return full_text
             
        except Exception as e:
             # Demo Fallback
             return (
                 f"⚠️ **Transcript Error**: {str(e)}\n\n"
                 "**[Demo Limit Reached] Using Sample Transcript:**\n"
                 "In this video, the speaker discusses the future of Generative AI. "
                 "They argue that while current models are impressive, the next leap "
                 "will come from embodied intelligence and robotics. Key points include "
                 "better reasoning capabilities and energy efficiency..."
             )

    except Exception as e:
        return f"System Error extracting YouTube: {str(e)}"
