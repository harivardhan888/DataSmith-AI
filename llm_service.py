
import os
import json
from groq import Groq
from dotenv import load_dotenv


load_dotenv(override=True)

class LLMService:

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        # Check if key is present AND not the placeholder
        if self.api_key and "gsk_" in self.api_key and "your_groq_api_key" not in self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                self.model_name = "llama-3.3-70b-versatile" 
            except Exception as e:
                print(f"Groq Init Error: {e}")
                self.client = None
        else:
            print("Using Simulation Mode (No valid key found)")

    def predict_intent(self, text: str, file_type: str = None) -> dict:
        # classify what the user wants
        if not self.client:
            return self._fallback_intent(text, file_type)

        try:
            # simple check first
            if not text and file_type:
                 return {
                    "intent": "unknown",
                    "needs_clarification": True,
                    "clarification_question": "I see the file. What should I do with it? (e.g. Summarize, Extract Text)",
                    "constraints": []
                }

            # Ask Llama 3
            system_prompt = """
            You are the 'Brain' of DataSmith Agent.
            Classify the User Request into one of: 
            ['summarize', 'sentiment', 'code_explain', 'extract_action_items', 'chat', 'unknown'].
            
            Rules:
            1. 'chat': General questions, greetings. 
            2. 'summarize': If user provides a file and asks "explain this", "what is this", "summarize".
            3. 'code_explain': If user uploads code/image and asks to explain it.
            4. 'unknown': 
               - If request is gibberish.
               - IF MISMATCH: User asks for creative writing (poem, song) but uploads technical code/data. In this case, return 'unknown' (or set clarification) to ask: "Do you want a poem ABOUT this code?"
            
            Output JSON: {"intent": "...", "needs_clarification": bool, "clarification_question": "...", "constraints": []}
            """
            
            user_content = f"User Input: '{text}'\nFile Type: {file_type if file_type else 'None'}"
            
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            return json.loads(completion.choices[0].message.content)

        except Exception as e:
            print(f"Intent Error: {e}")
            return self._fallback_intent(text, file_type)

    def generate_response(self, task: str, content: str, constraints: list = None) -> str:
        if not self.client:
            return self._mock_response(task, content)
            
        system_prompt = f"You are DataSmith. Task: {task}. Constraints: {constraints}. Output Text Only. Be helpful."
        
        # trim content if it's too huge
        truncated_content = content[:30000] 

        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Content:\n{truncated_content}\n\nPerform Task."}
                ],
                model=self.model_name,
                temperature=0.3
            )
            return completion.choices[0].message.content

        except Exception as e:
             print(f"Gen Error: {e}")
             return f"Error generating response: {e}"

    def _fallback_intent(self, text, file_type):
        # random basic logic if api fails
        text = text.lower()
        if "summarize" in text: return {"intent": "summarize", "needs_clarification": False, "constraints": []}
        if "sentiment" in text: return {"intent": "sentiment", "needs_clarification": False, "constraints": []}
        if "explain" in text: return {"intent": "code_explain" if "code" in text or "image" in str(file_type) else "summarize", "needs_clarification": False, "constraints": []}
        if not text and file_type: return {"intent": "unknown", "needs_clarification": True, "clarification_question": "What to do?", "constraints": []}
        return {"intent": "chat", "needs_clarification": False, "constraints": []}

    def _mock_response(self, task, content):
        return f"[Simulated Output]: Please check API Key."

    def transcribe_audio(self, audio_path: str) -> str:
        # use whisper
        if not self.client:
            return "[Error: API key missing]"
            
        try:
            with open(audio_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(os.path.basename(audio_path), file.read()),
                    model="whisper-large-v3", 
                    response_format="json", 
                    language="en"
                )
                return transcription.text
        except Exception as e:
            return f"Audio Error: {e}"
