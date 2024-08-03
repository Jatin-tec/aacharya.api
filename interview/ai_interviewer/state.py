class InterviewState:
    def __init__(self):
        self.state = {}
        self.conversation = []

    def update_state(self, new_data: dict):
        self.state.update(new_data)

    def get_state(self) -> dict:
        return self.state

    def set_state(self, state: dict):
        self.state = state

    def reset_state(self):
        self.state = {}

    def add_to_conversation(self, sender: str, message: str):
        self.conversation.append({'role': sender, 'parts': message})

    def get_conversation(self):
        return self.conversation
