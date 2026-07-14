"""
JD Generator agent.

Takes a 1-3 sentence job brief from HR and expands it into a professional
job description using Groq's LLM (llama-3.3-70b-versatile).
"""


def generate_jd(state: dict) -> dict:
    """
    LangGraph node. Reads state["job_brief"], calls Groq, writes
    the generated JD to state["job_description"].
    """
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate

    SYSTEM_PROMPT = """You are an expert HR copywriter. Generate a professional job description.
Include:
- Role summary (2-3 sentences)
- 5-7 key responsibilities
- Required qualifications
- Nice-to-haves

Format in plain text with clear section headings."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Generate a job description based on this brief:\n\n{job_brief}"),
    ])

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)
    chain = prompt | llm
    result = chain.invoke({"job_brief": state["job_brief"]})
    return {"job_description": result.content}
