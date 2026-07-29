# agents.py
import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url 
from dotenv import load_dotenv

load_dotenv(override=True)

# Configure LangChain to use OpenRouter's OpenAI-compatible API
llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.2
)

writer_llm = ChatOpenAI(
    model="openai/gpt-4o-mini", 
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.5 # Slightly higher temp for writing creativity
)

# 1. Search Agent (Using the modern create_agent)
def build_search_agent():
    return create_agent(model=llm, tools=[web_search])

# 2. Reader Agent (Using the modern create_agent)
def build_reader_agent():
    return create_agent(model=llm, tools=[scrape_url])

# 3. Writer Chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a PhD-level research writer. Write clear, structured, and insightful reports with proper inline citations [1], [2]."),
    ("human", """Write a detailed academic research draft on the topic below.

Topic: {topic}

Research Gathered:
{research}

Format strictly as Markdown:
# [Catchy Title]
## Executive Summary
## Detailed Findings (Use bullet points and bold text)
## Conclusion
## References (List actual URLs found in research)

Be factual, objective, and professional. Do NOT hallucinate sources."""),
])
writer_chain = writer_prompt | writer_llm | StrOutputParser()

# 4. Critic Chain (Evaluator)
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a strict, constructive academic reviewer. Your goal is to find flaws, missing citations, and formatting errors."),
    ("human", """Evaluate the following research draft.

Draft:
{report}

Provide your feedback in this format:
Score: X/10
Critique: [Paragraph explaining structural, factual, or formatting issues]
Actionable Revisions:
1. ...
2. ..."""),
])
critic_chain = critic_prompt | llm | StrOutputParser()

# 5. Reviser Chain (Self-Correction - THE 10/10 FEATURE)
reviser_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert editor. Your job is to take a draft and a critic's feedback, and rewrite the draft so it is perfect."),
    ("human", """Topic: {topic}

Original Draft:
{report}

Critic's Feedback:
{feedback}

Rewrite the entire report incorporating all the Critic's feedback. Ensure the final output is a polished, professional Markdown document with a flawless structure and accurate references."""),
])
reviser_chain = reviser_prompt | writer_llm | StrOutputParser()