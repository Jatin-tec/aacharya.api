from langgraph.graph import Graph, Node, Edge
from interviewer_module.functions import input_function, context_builder_function, question_generator_function, response_evaluator_function, follow_up_question_function, feedback_function

# Define nodes
input_node = Node(name="Input Node", function=input_function)
context_builder_node = Node(name="Context Builder Node", function=context_builder_function)
question_generator_node = Node(name="Question Generator Node", function=question_generator_function)
response_evaluator_node = Node(name="Response Evaluator Node", function=response_evaluator_function)
follow_up_question_node = Node(name="Follow-up Question Node", function=follow_up_question_function)
feedback_node = Node(name="Feedback Node", function=feedback_function)

# Define edges
edges = [
    Edge(source=input_node, target=context_builder_node),
    Edge(source=context_builder_node, target=question_generator_node),
    Edge(source=question_generator_node, target=response_evaluator_node),
    Edge(source=response_evaluator_node, target=follow_up_question_node, condition=needs_follow_up),
    Edge(source=follow_up_question_node, target=response_evaluator_node),
    Edge(source=response_evaluator_node, target=feedback_node, condition=interview_complete)
]

# Create and compile the graph
graph = Graph(nodes=[input_node, context_builder_node, question_generator_node, response_evaluator_node, follow_up_question_node, feedback_node], edges=edges)
compiled_graph = graph.compile()


if __name__ == "__main__":
    inputs = {
    "company_name": "OpenAI",
    "job_title": "Machine Learning Engineer",
    "job_description": "Responsible for developing ML models...",
    "resume": "John Doe's resume content..."
    }

    output = compiled_graph.run(inputs)
    print(output)
