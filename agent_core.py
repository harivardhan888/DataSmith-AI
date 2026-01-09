from llm_service import LLMService

class Agent:
    def __init__(self):
        self.llm = LLMService()
        self.history = []

    async def process_input(self, text_input: str, file_path: str = None, file_type: str = None, previous_context: dict = None):
        if text_input is None:
            text_input = ""
        
        # content extraction
        extracted_content = ""
        if file_path:
            from skills.processor import extract_content
            extracted_content = await extract_content(file_path, file_type)

        # check youtube
        if "youtube.com" in text_input or "youtu.be" in text_input:
            from skills.processor import extract_youtube_transcript
            words = text_input.split()
            for word in words:
                if "youtube.com" in word or "youtu.be" in word:
                    transcript = await extract_youtube_transcript(word)
                    if "Error" not in transcript and "Invalid" not in transcript:
                        extracted_content += f"\n\n[YouTube Transcript]:\n{transcript}"
                        file_type = "youtube_video" 
                    else:
                         extracted_content += f"\n\n[System: Could not fetch YouTube transcript. Error: {transcript}]"
                    break

        # handle clarification replies
        if previous_context and previous_context.get('needs_clarification'):
             combined_text = f"{previous_context.get('original_text', '')} {text_input}"
             text_input = combined_text
        
        # figure out intent
        intent_data = self.llm.predict_intent(text_input, file_type)
        print(f"DEBUG: Intent Detected: {intent_data}")

        if intent_data['needs_clarification']:
            return {
                "status": "clarification_needed",
                "output": intent_data['clarification_question'], # fixed typo
                "original_text": text_input,
                "extracted_content_snippet": extracted_content[:100] if extracted_content else ""
            }

        task = intent_data['intent']
        
        # chat / greeting logic
        print(f"DEBUG: text_input='{text_input}', len={len(text_input)}, task='{task}'")
        if task == "chat":
             # don't greet if file is present
             is_greeting = not text_input or len(text_input) < 5 or text_input.lower() in ['hi', 'hello', 'hey']
             
             if is_greeting and not file_path:
                 return {
                     "status": "success",
                     "output": "Hello! I am DataSmith AI. I can analyze texts, images, audio, and code. Upload a file or just chat with me.",
                     "extracted_text": extracted_content
                 }
             # general query fallback
             pass
        
        # validation
        if file_path and (not extracted_content or len(extracted_content.strip()) < 10):
            return {
                "status": "success",
                "output": "⚠️ I see you uploaded a file, but I couldn't extract any readable text from it. \n\n**Possible reasons:**\n1. It is a scanned PDF (image-only) and requires OCR.\n2. The file is empty.\n3. The format is not supported.\n\nPlease try a different file or a text-based PDF.",
                "extracted_text": "[No content extracted]"
            }

        # prep content
        if extracted_content:
            content_to_process = f"User Instruction: {text_input}\n\nTarget Content:\n{extracted_content}"
        else:
            content_to_process = text_input
        
        print(f"DEBUG: Generating response for task '{task}' with content len {len(content_to_process)}")
        result = self.llm.generate_response(task, content_to_process, intent_data.get('constraints', []))
        print(f"DEBUG: Final Result: '{result}'")
        
        return {
            "status": "success",
            "output": result,
            "extracted_text": extracted_content, 
            "intent_detected": task
        }
