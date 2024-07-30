from .models import InterviewSession
from .workflow import Workflow

class InterviewManager:
    def __init__(self, session_id):
        self.session = InterviewSession.objects.get(id=session_id)
        self.workflow = Workflow(self.session)

    def start_interview(self):
        # Initialize and start the interview process
        self.workflow.start()

    def process_response(self, user_input):
        # Handle user response and update the workflow
        self.workflow.handle_response(user_input)
        self.session.save()

    def get_current_question(self):
        # Get the current question or task from the workflow
        return self.workflow.get_current_question()
