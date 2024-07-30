from langgraph.graph import Graph
from typing import Optional, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("LLM_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)

class Questions(BaseModel):
    technical_questions: Optional[list[str]] = Field(..., description="List of technical questions to evaluate the candidate", title="Technical Questions")
    experience_based_questions: Optional[list[str]] = Field(..., description="List of questions to evaluate the candidate's experience", title="Experience Based Questions")
    job_specific_questions: Optional[list[str]] = Field(..., description="List of questions specific to the job role", title="Job Specific Questions")
    general_questions: Optional[list[str]] = Field(..., description="General questions to evaluate the candidate", title="General Questions")

class AgentState(TypedDict):
    questions: Questions

def input_function(inputs):
    return inputs

def context_builder_function(inputs):
    context = f"Company: {inputs['company_name']} Job Title: {inputs['job_title']} Job Description: {inputs['job_description']} Resume: {inputs['resume']}"
    return context

def question_generator_function(context):
    parser = PydanticOutputParser(pydantic_object=Questions)
    prompt = PromptTemplate(
        template="""
        Generate a list of questions based on the following context to evaluate the candidate.
        {format_instructions}
        -------
        {context}
        ------
        """,
        input_variables=["context"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | llm | parser
    return chain.invoke({"context": context})


workflow = Graph()

workflow.add_node("input", input_function)
workflow.add_node("context_builder", context_builder_function)
workflow.add_node("question_generator", question_generator_function)

workflow.add_edge("input", "context_builder")
workflow.add_edge("context_builder", "question_generator")

workflow.set_entry_point("input")
workflow.set_finish_point("question_generator")

app = workflow.compile()

message = app.invoke({
    "company_name": "Google",
    "job_title": "Data Analyst",
    "job_description": """"
    Minimum qualifications:

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
    """,
    "resume": """
    Jatin Kshatriya ♂phone+91-8878249595
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
    •Samart India Hackathon - 2022: national finalists. 08/2022
    """
})

print(message)

# parser = PydanticOutputParser(pydantic_object=Questions)
# print(parser.get_format_instructions())