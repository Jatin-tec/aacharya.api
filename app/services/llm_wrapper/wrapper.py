import time
import openai
import dotenv
import os
from .prompts.system_prompt import get_system_prompt, get_notes_generator_prompt, get_categories_prompt


class LLMWrapper:
    """Wrapper class for the LLM API."""
    def __init__(self, max_tokens=1000, model="gpt-3.5-turbo", max_tries=2, temperature=0):
        self.max_tokens = max_tokens
        self.model = model
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
        self.history.append({"role": "system", "content": system_prompt})

    def _send_request(self, user_prompt, **kwargs):
        # Append the user prompt to history after the system's initial response setup
        self.history.append({"role": "user", "content": user_prompt})

        for attempt in range(self.max_tries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=self.history,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                # Append the model's response to history
                self.history.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
                
                summary = kwargs.get('summary', False)
                categorize = kwargs.get('categorize', False)

                if summary:
                    print(self.history, "history")
                    self.reset_history()

                if categorize:
                    print(self.history, "history")
                    self.reset_history()

                print(self.history)
                return response['choices'][0]['message']['content']

            except openai.error.RateLimitError as e:
                print("Rate limit exceeded, retrying...", e)
                if attempt < self.max_tries - 1:
                    self._handle_rate_limit()
                else:
                    return {'error': 'rate_limit_exceeded', 'message': str(e)}

            except openai.error.InvalidRequestError as e:
                print("Invalid request:", e)
                return {'error': 'invalid_request', 'message': str(e)}

            except Exception as e:
                print("Unhandled exception:", e)
                return {'error': 'unknown', 'message': str(e)}
    
    def _handle_rate_limit(self):
        time.sleep(10)

    def generate_response(self, user_input, **kwargs):
        if not self.history:
            self._prepare_system_prompt(user_input, **kwargs)
        return self._send_request(user_input, **kwargs)

    def reset_history(self):
        self.history = []

if __name__ == "__main__":
    dotenv.load_dotenv()
    openai.api_key = os.getenv("OPENAI_APIKEY")
    API_TOKEN = os.getenv("HUGGINGFACE_APIKEY")

    wrapper = LLMWrapper()
    
    index = 0
    while True:
        user_input = input("\nUser: ")    
        response = wrapper.generate_response(user_input)

        response_msg = ""
        for r in response:
            if r["choices"][0]["delta"] == {}:
                break
            msg = r["choices"][0]["delta"]["content"]
            response_msg += msg
            print(msg, end="", flush=True)

        wrapper.history.append({
            "role": "user", 
            "content": response_msg
        })
        index += 1
