RESPONSE_EVALUATION_PROMPT = """
Evaluate the candidate's response to the following, 
    Question: {question}
    Response: {response}
--------------------
Previous conversation: {conversation}
--------------------
Response format:
    -> feedback: A brief feedback on the response.
    -> score: A score between 0 and 10.
    -> next_node: The next node to move to in the conversation, 
        Options: (
        FeedbackNode-> If user doesn't knows the answer or requires further clarification on the question or you want to praise the user choose this option.
        AskQuestionNode -> If everthing seems fine move to the next question.
        )
--------------------
JSON response example:
{{
    "feedback": "The response was good and to the point.",
    "score": 7,
    "next_node": "AskQuestionNode"
}}
Only give JSON response, i.e. an object with the keys "feedback", "score" and "next_node". No styling or additional text.
"""

def get_response_evaluation_prompt(question: str, response: str, conversation: list) -> str:
    return RESPONSE_EVALUATION_PROMPT.format(question=question, response=response, conversation=conversation)

FEEDBACK_PROMPT = """
Provide feedback to the candidate based on the response to the following question:
    Question: {question}
    Response: {response}
--------------------
Previous conversation: {conversation}
--------------------
Feedback format:
    -> feedback: A brief feedback on the response or the candidate's performance, you can also ask a follow-up question explaining the feedback.
    -> next_node: The next node to move to in the conversation, 
        Options: (
        ResponseNode -> If you want to ask the candidate another question or candidate needs to provide more details.
        AskQuestionNode -> If everthing seems fine move to the next question.
        )
--------------------
IMPORTANT: 
-> You must not provide answers to the questions. 
-> If candidate asks for the answer, you must say that you are not allowed to provide the answer.
-> Feedback should feel like constructive continuation of the conversation.
--------------------
JSON response example:
{{
    "feedback": "That was a good response, but you can improve by providing more details.",
    "next_node": "AskQuestionNode"
}}
Only give JSON response, i.e. an object with the keys "feedback", "score" and "next_node". No styling or additional text.
"""

def get_feedback_prompt(question: str, response: str, conversation: list) -> str:
    return FEEDBACK_PROMPT.format(question=question, response=response, conversation=conversation)