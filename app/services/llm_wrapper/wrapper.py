import time
import openai
import dotenv
import os
from .prompts.system_prompt import get_system_prompt, get_notes_generator_prompt

class LLMWrapper:
    """Wrapper class for the LLM API."""
    def __init__(self, max_tokens=1000, model="gpt-3.5-turbo", max_try=2, temprature=0):
        self.max_tokens = max_tokens
        self.model = model
        self.temperature = temprature
        self.max_try = max_try
        self.history = [
            {"role": "system", "content": ""}, 
        ]

    def _send_request(self, user_prompt="", context=None, vectorstore=None, summary=False, questions=None):
        for _ in range(self.max_try):
            try:
                self.history.append({"role": "user", "content": f"{user_prompt}"}) 

                if vectorstore:
                    collection = vectorstore.get_collection(name="FAQ", embedding_function=huggingface_ef)
                    context = collection.query(
                        query_texts=user_prompt,
                        n_results=4
                    )
                
                self.history[0]["content"] = get_system_prompt(context)
                if summary:
                    self.history[0]["content"] = get_notes_generator_prompt(context, questions)

                print(self.history, "printing general chat prompt")
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=self.history,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    stream=True,
                )
                return response 

            except openai.error.RateLimitError as e:
                print(e)
                self._handle_rate_limit()
                return self._send_request(context)
            
            except openai.error.InvalidRequestError as e:
                if len(prompt) > self.max_tokens:
                    print("Prompt too long. Truncating...")
                    prompt = prompt[:self.max_tokens]
                    return self._send_request(prompt, context)
                print("Invalid request:", e)
                return {'error': 'invalid_request'}
            
            except Exception as e:
                print("Unhandled exception:", e)
                return {'error': 'unknown'}

    def _handle_rate_limit(self):
        print("Rate limit exceeded. Waiting before retrying...")
        time.sleep(60) 

    def generate_response(self, user_input, context=None, vectorstore=None, summary=False, questions=None):
        response = self._send_request(user_input, context, vectorstore, summary, questions)
        return response

    def reset_history(self):
        self.history = False

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