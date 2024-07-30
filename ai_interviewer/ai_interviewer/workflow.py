from langgraph.graph import Graph
from ai_interviewer.functions import input_function, context_builder_function, question_generator_function, response_evaluator_function, follow_up_question_function, feedback_function, needs_follow_up, interview_complete

class Workflow:
    def __init__(self, session):
        self.session = session
        self.graph = self._initialize_graph()

    def _initialize_graph(self):
        graph = Graph()
        
        nodes = {
            'Start': {'type': 'initial', 'action': 'initialize_context'},
            'Ask Screening Question': {'type': 'action', 'action': 'ask_screening_question'},
            'Evaluate Resume': {'type': 'action', 'action': 'evaluate_resume'},
            'Ask Technical Question': {'type': 'action', 'action': 'ask_technical_question'},
            'End': {'type': 'final', 'action': 'end_interview'}
        }
        edges = [
            ('Start', 'Ask Screening Question'),
            ('Ask Screening Question', 'Evaluate Resume'),
            ('Evaluate Resume', 'Ask Technical Question'),
            ('Ask Technical Question', 'End')
        ]
        
        for node, data in nodes.items():
            graph.add_node(node, data)
        for edge in edges:
            graph.add_edge(edge[0], edge[1])
        
        graph.set_entry_point('Start')
        graph.set_finish_point('End')

        app = graph.compile()
        return app

    def start(self):
        # Initialize and start the workflow
        self.session.current_node = 'Start'
        self.session.save()

    def handle_response(self, user_input):
        # Update the workflow based on user input
        current_node = self.session.current_node
        next_node = self.graph.get_next_node(current_node, user_input)
        self.session.current_node = next_node
        self.session.save()

    def get_current_question(self):
        # Get the current question or task from the workflow
        current_node = self.session.current_node
        return self.graph.get_node_action(current_node)
