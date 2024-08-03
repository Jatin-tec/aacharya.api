from typing import Dict, Optional, List
from interview.ai_interviewer.state import InterviewState
from interview.ai_interviewer.prompts import get_response_evaluation_prompt, get_feedback_prompt
import google.generativeai as genai
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from interview.models import InterviewConversation, Interview
import json
import os

genai.configure(api_key=os.getenv("LLM_API_KEY"))
llm = genai.GenerativeModel(model_name='gemini-1.5-flash')

class InterviewNode:
    def __init__(self, node_name: str, consumer, requires_input: bool = False):
        self.node_name = node_name
        self.consumer = consumer
        self.requires_input = requires_input

    async def run(self, state: InterviewState) -> Optional[str]:
        raise NotImplementedError("Each node must implement a run method.")

class IntroNode(InterviewNode):
    def __init__(self, consumer):
        super().__init__("IntroNode", consumer)

    async def run(self, state: InterviewState, **kwargs) -> Optional[str]:
        response = "Hello and welcome to the interview, I'm your interviewer today. Please introduce yourself."
        state.add_to_conversation('model', response)
        await self.send_to_client(state, response)
        return "ResponseNode"  # Moving to a node that will handle user response

    async def send_to_client(self, state: InterviewState, message: str):
        await self.consumer.send(text_data=json.dumps({
            'response': message,
            'conversation': state.get_conversation()
        }))

class ResponseNode(InterviewNode):
    def __init__(self, consumer):
        super().__init__("ResponseNode", consumer, requires_input=True)
    
    async def run(self, state: InterviewState, **kwargs) -> Optional[str]:
        user_input = kwargs.get("user_input")
        print(kwargs, "kwargs")
        if user_input:
            # Update state with user input
            state.update_state({"user_input": user_input})
            state.add_to_conversation('user', user_input)
            return "EvaluationNode"
        return None
    
class EvaluationNode(InterviewNode):
    def __init__(self, consumer):
        super().__init__("EvaluationNode", consumer)

    async def run(self, state: InterviewState, **kwargs) -> Optional[str]:
        question = state.get_conversation()[-2]
        user_response = state.get_conversation()[-1]
        conversation = state.get_conversation()[:-2]
        system_prompt = get_response_evaluation_prompt(question, user_response, conversation)

        # Generate response using LLM
        llm_response = await self.generate_llm_response(system_prompt)

        print(llm_response.text, "llm response")
        response_data = json.loads(llm_response.text)
        
        # Save conversation data to database
        await self.save_interview_data(state, question, user_response, response_data)

        next_node = response_data.get("next_node")
        return next_node
    
    async def generate_llm_response(self, system_prompt):
        # Assuming llm.generate_content is synchronous, use sync_to_async
        return await sync_to_async(llm.generate_content)({
            "role": "user",
            "parts": [system_prompt]
        })

    @database_sync_to_async
    def save_interview_data(self, state, question, user_response, response):
        interview_instance = Interview.objects.get(interview_code=state.get_state().get("interview_code"))
        InterviewConversation.objects.create(
            interview=interview_instance,
            question=question,
            response=user_response,
            feedback=response.get("feedback"),
            score=response.get("score")
        ).save()

class AskQuestionNode(InterviewNode):
    def __init__(self, consumer, questions: Optional[List[str]] = None):
        super().__init__("AskQuestionNode", consumer)
        self.questions = questions if questions else []

    async def run(self, state: InterviewState, **kwargs) -> Optional[str]:
        question_index = state.get_state().get("question_index", 0)
        if question_index < len(self.questions):
            response = self.questions[question_index]
            state.add_to_conversation('model', response)
            state.update_state({"question_index": question_index + 1})
            await self.send_to_client(state, response)
            return "ResponseNode"  # Moving to a node that will handle user response
        else:
            return "EndNode"
    
    async def send_to_client(self, state: InterviewState, message: str):
        await self.consumer.send(text_data=json.dumps({
            'response': message,
            'conversation': state.get_conversation()
        }))


class FeedbackNode(InterviewNode):
    def __init__(self, consumer):
        super().__init__("FeedbackNode", consumer)

    async def run(self, state: InterviewState, **kwargs) -> Optional[str]:
        question = state.get_conversation()[-2]
        response = state.get_conversation()[-1]
        chat_history = state.get_conversation()[:-2]
        system_prompt = get_feedback_prompt(question, response, chat_history)
        response = llm.generate_content({
            "role": "user",
            "parts": [system_prompt]
        })
        print(response.text, "llm response")
        response = json.loads(response.text)
        next_node = response.get("next_node")
        answer = response.get("feedback")
        state.add_to_conversation('model', answer)
        await self.send_to_client(state, answer)
        return next_node

    async def send_to_client(self, state: InterviewState, message: str):
        await self.consumer.send(text_data=json.dumps({
            'response': message,
            'conversation': state.get_conversation()
        }))

class EndNode(InterviewNode):
    def __init__(self, consumer):
        super().__init__("EndNode", consumer)

    async def run(self, state: InterviewState, **kwargs) -> Optional[str]:
        response = "Thank you for participating in the interview. Goodbye!"
        state.add_to_conversation('model', response)
        await self.send_to_client(state, response)
        return None

    async def send_to_client(self, state: InterviewState, message: str):
        await self.consumer.send(text_data=json.dumps({
            'response': message,
            'conversation': state.get_conversation()
        }))
