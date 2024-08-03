from typing import Dict
from interview.ai_interviewer.nodes import InterviewNode
from interview.ai_interviewer.state import InterviewState

class InterviewManager:
    def __init__(self, nodes: Dict[str, InterviewNode], initial_node: str, state: InterviewState):
        self.nodes = nodes
        self.current_node_name = initial_node
        self.state = state

    async def run(self):
        while self.current_node_name is not None:
            current_node = self.nodes[self.current_node_name]
            self.current_node_name = await current_node.run(self.state)

    def get_current_state(self) -> dict:
        return self.state.get_state()

    def set_state(self, state: dict):
        self.state.set_state(state)
