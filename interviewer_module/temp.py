from langchain_core.prompts import ChatPromptTemplate

def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    # functions = [format_tool_to_openai_function(t) for t in tools]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "user",
                """You are an AI assistant, collaborating with other assistants.
                 Use the provided tools to progress towards answering the question: {tool_names}.
                 If you are unable to fully answer correctly, there is no problem, another assistant with different tools 
                 will help where you left off. 
                 If you or any of the other assistants have the final answer or deliverable, use the generated json as source of data and
                 prefix your response with FINAL ANSWER so the team knows to stop.
                 Double check the answer. Do not provide incomplete answers!
                 You have access to the following tools: Use {tool_names} to gather data.\n Use {system_message} to guide you in your task."""
            ),
            ("system","{messages}"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    return prompt | llm.bind_functions()