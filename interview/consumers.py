from channels.generic.websocket import AsyncWebsocketConsumer
from interview.ai_interviewer.manager import InterviewManager
from interview.ai_interviewer.nodes import IntroNode, ResponseNode, EvaluationNode, AskQuestionNode, FeedbackNode, EndNode
from interview.ai_interviewer.state import InterviewState
from interview.models import Interview
import json

class InterviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.interview_id = self.scope['url_route']['kwargs']['interview_id']
        self.state = InterviewState()

        # Initialize nodes with generative model and pass the consumer reference
        self.nodes = {
            "IntroNode": IntroNode(self),
            "ResponseNode": ResponseNode(self),
            "EvaluationNode": EvaluationNode(self),
            "AskQuestionNode": AskQuestionNode(self, ["What are your strengths?", "What is your biggest weakness?"]),
            "FeedbackNode": FeedbackNode(self),
            "EndNode": EndNode(self)
        }

        self.manager = InterviewManager(self.nodes, "IntroNode", self.state)
        self.state.update_state({"interview_code": self.interview_id})
        await self.accept()
        await self.run_node(self.manager.current_node_name)

    async def disconnect(self, close_code):
        # Handle disconnection
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json, "text_data_json")
        user_input = text_data_json.get('message')
        # Move to ResponseNode with user input
        await self.run_node(self.manager.current_node_name, user_input=user_input)

    async def run_node(self, node_name, **kwargs):
        current_node = self.nodes.get(node_name)
        if current_node:
            print(f"Running node: {node_name}")
            print(f"Current state: {self.state.get_state()}")
            print(f"Conversation: {self.state.get_conversation()}")
            if not current_node.requires_input or kwargs.get("user_input"):
                next_node_name = await current_node.run(self.state, **kwargs)
                self.manager.current_node_name = next_node_name
                if next_node_name:
                    await self.run_node(next_node_name)
                else:
                    await self.send(text_data=json.dumps({
                        'response': 'Interview process ended.',
                        'conversation': self.state.get_conversation()
                    }))
        else:
            await self.send(text_data=json.dumps({
                'response': 'Invalid node.',
                'conversation': self.state.get_conversation()
            }))
