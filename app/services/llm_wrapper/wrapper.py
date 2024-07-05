import os
import time
import dotenv
import google.generativeai as genai
from .prompts.system_prompt import get_system_prompt, get_notes_generator_prompt, get_categories_prompt

class LLMWrapper:
    """Wrapper class for the LLM API."""
    def __init__(self, max_tokens=1000, model="gemini-1.5-flash", max_tries=2, temperature=0):
        self.max_tokens = max_tokens
        self.model = genai.GenerativeModel(model)
        self.temperature = temperature
        self.max_tries = max_tries
        self.history = []

    def _prepare_system_prompt(self, user_prompt, **kwargs):
        # System prompt before appending the user prompt to history
        context = kwargs.get('context')
        vectorstore = kwargs.get('vectorstore')
        summary = kwargs.get('summary', False)
        categorize = kwargs.get('categorize', False)
        questions = kwargs.get('questions')

        if vectorstore:
            pass
            # collection = vectorstore.get_collection(name="FAQ", embedding_function="huggingface_ef")
            # context = collection.query(query_texts=user_prompt, n_results=4)

        system_prompt = get_system_prompt(context)
        if summary:
            current = kwargs.get('current', 1)
            total = kwargs.get('total', 1)
            system_prompt = get_notes_generator_prompt(context, questions, current, total)

        if categorize:
            transcript = kwargs.get('script')
            description = kwargs.get('video_description')
            system_prompt = get_categories_prompt(transcript, description)

        # Append the system prompt first in a new conversation
        self.history.append({"role": "user", "parts": [system_prompt]})

    def _send_request(self, user_prompt, **kwargs):
        # Append the user prompt to history after the system's initial response setup
        self.history.append({"role": "user", "parts": [user_prompt]})

        for attempt in range(self.max_tries):
            try:
                response = self.model.generate_content(self.history)
                print(response)

                # Append the model's response to history
                self.history.append({"role": "model", "parts": [response.text]})
                
                summary = kwargs.get('summary', False)
                categorize = kwargs.get('categorize', False)

                if summary:
                    self.reset_history()

                if categorize:
                    self.reset_history()

                return response.text
            
            except genai.exceptions.RateLimitException:
                if attempt == 0:
                    sleep_time = 0
                if attempt == self.max_tries - 1:
                    return {'error': 'rate_limit', 'message': 'Rate limit exceeded'}
                self._handle_rate_limit(sleep_time+10)
            
            except Exception as e:
                print("Unhandled exception:", e)
                return {'error': 'unknown', 'message': str(e)}
    
    def _handle_rate_limit(self, sleep_time=10):
        time.sleep(sleep_time)

    def generate_response(self, user_input, **kwargs):
        if not self.history:
            self._prepare_system_prompt(user_input, **kwargs)
        return self._send_request(user_input, **kwargs)

    def reset_history(self):
        self.history = []