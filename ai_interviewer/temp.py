from typing import TypedDict, Optional , List

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("LLM_API_KEY")

# Setting up the LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)

# Define the schema for the questions
class Questions(BaseModel):
    technical_questions: List[str] = Field(..., description="Technical questions")
    experience_based_questions: List[str] = Field(..., description="Experience based questions")
    job_specific_questions: List[str] = Field(..., description="Job-specific questions")
    general_questions: List[str] = Field(..., description="General questions")

class Evaluation(BaseModel):
    score: float = Field(..., description="Score of the candidate")
    feedback: str = Field(..., description="Feedback for the candidate")
    next_steps: str = Field(..., description="""Next steps for the candidate it'll be a single word from following choices: 
                            `feedback`-> if the user is confused about the question or user doesn't know then answer this should be choosen
                            `next_question`-> if the user has answered the question correctly and the interviewer wants to ask the next question
                            `follow_up`-> if the user has answered the question correctly and the interviewer wants to ask the follow-up question
                            `end`-> if the user has answered all the questions and the interview is over""")

class GraphState(TypedDict):
    messages: Optional[List[str]]
    response: HumanMessage
    context: str
    questions: Optional[Questions]
    evaluation: Optional[str]

# Function to generate questions based on the context
def generate_questions(state: GraphState):
    parser = PydanticOutputParser(pydantic_object=Questions)
    prompt = PromptTemplate(
        template="""
        Generate a list of questions based on the following context to evaluate the candidate.
        -------
        {context}
        ------
        {format_instructions}
        """,
        input_variables=["context", "format_instructions"],
    )
    model = prompt | llm | parser
    questions = model.invoke({"context": state["context"], "format_instructions": parser.get_format_instructions()})
    print(questions, "questions")
    state["questions"] = questions
    return state

# Function to ask the candidate to introduce themselves
def ask_intro(state: GraphState):
    state["messages"].append("Please introduce yourself.")
    return state

# Function to get feedback from the user
def user_feedback(state: GraphState):
    return state

# Function to ask a question from the list or a follow-up question
def ask_question(state: GraphState):
    question_list = state.get("questions", {}).get("general_questions", [])
    follow_up = state.get("follow_up_question", None)
    question = follow_up or question_list.pop(0) if question_list else "No more questions."
    state["questions"]["general_questions"] = question_list
    state["current_question"] = question
    prompt = PromptTemplate(
        template="Question: {question}",
        input_variables=["question"],
    )
    chain = prompt | llm
    return chain.invoke({"question": question})

# Function to evaluate the candidate's response
def evaluate_response(state: GraphState):
    prompt = PromptTemplate(
        template="""Evaluate the candidate's response to the following, 
        Question: {question}
        Response: {response}
        --------------------
        {format_instructions}
        """,
        input_variables=["question", "response", "format_instructions"],
    )
    parser = PydanticOutputParser(pydantic_object=Evaluation)
    state["messages"].append(state["response"])
    chain = prompt | llm
    score = chain.invoke({"response": state["response"], "question": state["messages"][-2], "format_instructions": parser.get_format_instructions()})
    state["evaluation"] = score
    return state

# Conditional function to determine the next step
def decide_next(state: GraphState):
    if state["evaluation"]["next_steps"] == "feedback":
        return "user_feedback"
    elif state["evaluation"]["next_steps"] == "next_question":
        return "ask_question"
    elif state["evaluation"]["next_steps"] == "follow_up":
        return "ask_question" 
    return END
    

# Initialize the graph and add nodes and edges
workflow = StateGraph(GraphState)

workflow.add_node("generate_questions", generate_questions)
workflow.add_node("ask_intro", ask_intro)
# workflow.add_node("ask_question", ask_question)
workflow.add_node("user_feedback", user_feedback)
workflow.add_node("evaluate_response", evaluate_response)

workflow.add_edge(START, "generate_questions")
workflow.add_edge("generate_questions", "ask_intro")
workflow.add_edge("ask_intro", "user_feedback")
workflow.add_edge("user_feedback", "evaluate_response")
workflow.add_edge("evaluate_response", END)

# workflow.add_edge("ask_question", "evaluate_response")
# workflow.add_conditional_edges("evaluate_response", decide_next, {"ask_question": "ask_question", END: END})

# Set entry and finish points
# workflow.set_entry_point("generate_questions")
# workflow.set_finish_point(END)

# Initialize memory to persist state
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer, interrupt_before=["user_feedback"])
# display(Image(graph.get_graph().draw_mermaid_png()))


thread = {"configurable": {"thread_id": "1"}}

initial_input = {"context": """
    "company_name": "Google",
    "job_title": "Data Analyst",
    "job_description": "Minimum qualifications:
        Bachelor's degree or equivalent practical experience.
        2 years of experience in data analytics, Trust & Safety, policy, cybersecurity, or related fields.
        Experience in SQL, building dashboards, data collection and transformation, statistical modeling, visualization and dashboards, or a scripting or programming language (e.g., Python, Java, C++).
        Experience in writing and maintaining ETLs (Extract, Transform, Load) that operate on a range of structured and unstructured sources.
        Experience in leveraging data to derive meaningful insights and actionable recommendations.

        Preferred qualifications:
        Education in, or experience with, machine learning.
        Experience in SQL, building dashboards, data collection/transformation, visualization/dashboards, or in a scripting/programming language (e.g., Python).
        Excellent communication and presentation skills (written and verbal) and the ability to influence cross-functionally at various levels.
        Excellent problem-solving and critical thinking skills with attention to detail in an ever-changing environment.

        About the jobTrust & Safety team members are tasked with identifying and taking on the biggest problems that challenge the safety and integrity of our products. They use technical know-how, excellent problem-solving skills, user insights, and proactive communication to protect users and our partners from abuse across Google products like Search, Maps, Gmail, and Google Ads. On this team, you're a big-picture thinker and strategic team-player with a passion for doing what’s right. You work globally and cross-functionally with Google engineers and product managers to identify and fight abuse and fraud cases at Google speed - with urgency. And you take pride in knowing that every day you are working hard to promote trust in Google and ensuring the highest levels of user safety.

        Within Trust and Safety, the Service Delivery team is responsible for the strategy, governance, and operations across the Temp, Vendor, and Contractor (TVC) population. Partnering with teams across Legal, Security, Extended Workforce Solutions (xWS), REWS, Trust and Safety (T&S), Engineering, and external Vendor partners to bring innovation and technology in building operations and protecting users. Service Delivery (SD) team members have the opportunity to create, develop, and implement some of the most complex operations.At Google we work hard to earn our users’ trust every day. Trust & Safety is Google’s team of abuse fighting and user trust experts working daily to make the internet a safer place. We partner with teams across Google to deliver bold solutions in abuse areas such as malware, spam and account hijacking. A diverse team of Analysts, Policy Specialists, Engineers, and Program Managers, we work to reduce risk and fight abuse across all of Google’s products, protecting our users, advertisers, and publishers across the globe in over 40 languages.

        Responsibilities
        Design, develop, and maintain Trust and Safety access and security systems, ensuring that security objectives are fully achieved without compromising operational efficiency.
        Design and implement seamless integrations between business goals and security systems, including the development and execution of strategies that support the effectiveness of these systems.
        Manage projects that involve multiple stakeholders, have stringent deadlines, hold significant implications for the organization, and require adaptability to changing circumstances.
        Demonstrate an understanding of the process area, encompassing domain expertise in data sources, access and authentication methods, and relevant products.

        Google is proud to be an equal opportunity workplace and is an affirmative action employer. We are committed to equal employment opportunity regardless of race, color, ancestry, religion, sex, national origin, sexual orientation, age, citizenship, marital status, disability, gender identity or Veteran status. We also consider qualified applicants regardless of criminal histories, consistent with legal requirements. See also Google's EEO Policy and EEO is the Law. If you have a disability or special need that requires accommodation, please let us know by completing our Accommodations for Applicants form .
        ",
        "resume": "Jatin Kshatriya ♂phone+91-8878249595
        Portfolio: jatin-tec.github.io /envel⌢pejatin.kshatriya2821@gmail.com
        Bachelor of Technology /githubGitHub Profile
        Samrat Ashok Technological Institute, Vidisha /linkedinLinkedIn Profile
        Experience
        •Happy Monk 7/2023- 10/2023
        Data Engineer Remote Internship
        –Developed the inference pipeline of an advanced video analytics solution, resulting in a 30% improvement in
        processing speed and a 20% increase in accuracy.
        –Engineered the Bagdogra pipeline for a military base, ensuring reliable detection and alarming of elephants and
        classification of civilians and soldiers in an offline environment, enhancing local security measures.
        •Mastork 5/2023 - 6/2023
        Backend Developer Remote Internship
        –Streamlinedcodebaseandimprovedperformanceby30%throughtheimplementationofDjangoclass-basedgeneric
        views and serializers.
        –Helped the DevOps team in deployment by dockerizing the entire application, saving 25% of deployment time.
        •Kaizen Young Consultant 2/2022 - 1/2023
        Full Stack Developer Remote Internship
        –Enhanced educational website My Question Box by implementing additional features and database migration,
        leading to improved functionality and user experience.
        –Maintained and updated the CMS of the News app Live VNS, resulting in streamlined operations and contributing
        to over 100K downloads on the Play Store.
        –Led a team of frontend and backend developers and a designer, to architect and build the startup Billify, ensuring
        seamless integration and efficient performance.
        Education
        •Bachelor of Technology in Artificial Intelligence and DataScience 2020-2024
        Samrat Ashok Technological Institute, Vidisha CGPA: 8.2
        Personal Projects
        •Lossy Image Compression and Decompression Live Link: Project Report
        A project focused on developing an efficient image compression system using autoencoders.
        –Developed a CNN-based autoencoder for image compression, achieving a 91.67% reduction in data size while
        maintaining a PSNR of 22dB and SSIM of 0.85.
        –Implemented regularization and data augmentation techniques, reducing overfitting by 25% and improving model
        generalization on unseen data.
        –Potential to revolutionize image storage and retrieval, enabling more efficient use of storage resources and faster
        access to high-quality images.
        •Aacharya Live Link: aacharya.in
        Personalized Adaptive E-learning Platform
        –Developed a platform with real-time video interactions, personalized suggestions and a dashboard for tracking
        learning progress.
        –Won prizes in two hackathons back-to-back for innovative design and functionality.
        –Potential annual revenue of over 433 Crore (B2B and B2C).
        Technical Skills
        Languages : Python, Javascript
        Tools: Tensorflow, Keras, PyTorch, Git, Github, Docker, Linux
        Frameworks : Django, Flask, Streamlit, NextJs
        Cloud/Databases :MongoDb, Relational Database(mySql), Chroma(Vector DB), Firebase, AWS, CI/CD
        Achievements
        •Student Data Science Championship: first runner-up among 1200 participants. 05/2024
        •Sprint Hacks 2.0: first runner-up position out of over 2700 registered teams. 05/2024
        •Witty Hacks 4.0: Winner among top 40 teams. 04/2024
        •Samart India Hackathon - 2022: national finalists. 08/2022"
    """, 
    "messages": [],
    }

# Run the graph until the first interruption
for event in app.stream(initial_input, thread, stream_mode="values"):
    print(event)
user_input = input("Tell me about yourself: ")
app.update_state(thread, {"response": user_input}, as_node="user_feedback")
for event in app.stream(None, thread, stream_mode="values"):
    print(event)
