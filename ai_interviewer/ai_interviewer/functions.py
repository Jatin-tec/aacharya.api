def input_function(inputs):
    # Extract and return inputs (company name, job title, job description, resume)
    return inputs

def context_builder_function(inputs):
    # Construct the context for the LLM
    context = f"Company: {inputs['company_name']}, Job Title: {inputs['job_title']}, Job Description: {inputs['job_description']}, Resume: {inputs['resume']}"
    return context

def question_generator_function(context):
    # Generate initial interview questions based on context
    questions = generate_questions_from_context(context)
    return questions

def response_evaluator_function(questions, responses):
    # Evaluate user responses and decide on follow-up questions
    follow_up_needed = evaluate_responses(questions, responses)
    return follow_up_needed

def follow_up_question_function(responses):
    # Generate follow-up questions based on previous responses
    follow_up_questions = generate_follow_up_questions(responses)
    return follow_up_questions

def feedback_function(evaluation):
    # Provide feedback to the user
    feedback = generate_feedback(evaluation)
    return feedback

def needs_follow_up(evaluation):
    # Condition to check if follow-up questions are needed
    return evaluation['follow_up_needed']

def interview_complete(evaluation):
    # Condition to check if the interview is complete
    return not evaluation['follow_up_needed']
