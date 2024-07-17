import time
import google.generativeai as genai
from llm_wrapper.settings import LLM_API_KEY
from .prompts.system_prompt import get_system_prompt, get_notes_generator_prompt, get_categories_prompt, get_visualization_prompt

class LLMWrapper:
    """Wrapper class for the LLM API."""
    def __init__(self, max_tokens=1000, model="gemini-1.5-flash", max_tries=2, temperature=0):
        genai.configure(api_key=LLM_API_KEY)
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
        visualize = kwargs.get('visualize', False)
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
        
        if visualize:
            system_prompt = get_visualization_prompt(context)

        # Append the system prompt first in a new conversation
        self.history.append({"role": "user", "parts": [system_prompt]})

    def _send_request(self, user_prompt, **kwargs):
        # Append the user prompt to history after the system's initial response setup
        self.history.append({"role": "user", "parts": [user_prompt]})
        print(self.history)
        for _ in range(self.max_tries):
            try:
                response = self.model.generate_content(self.history)
                # Append the model's response to history
                self.history.append({"role": "model", "parts": [response.text]})
                
                summary = kwargs.get('summary', False)
                categorize = kwargs.get('categorize', False)

                if summary:
                    self.reset_history()

                if categorize:
                    self.reset_history()

                return response.text
            
            except Exception as e:
                print("Unhandled exception:", e)
                return {'error': 'unknown', 'message': str(e)}
    
    def _handle_rate_limit(self, sleep_time=10):
        time.sleep(sleep_time)

    def generate_response(self, user_input, **kwargs):
        """
        The function generates a response based on user input and system prompts.
        
        :param user_input: The `user_input` parameter in the `generate_response` method represents the
        input provided by the user. This input is used by the method to generate a response or perform
        some action based on the user's input
        context: The `context` parameter in the `generate_response` method represents the context of the
        conversation. This context is used to provide additional information to the model to generate a
        more accurate response.
        :return: The `generate_response` method returns the result of the `_send_request` method.
        """
        if not self.history:
            self._prepare_system_prompt(user_input, **kwargs)
        return self._send_request(user_input, **kwargs)

    def reset_history(self):
        self.history = []