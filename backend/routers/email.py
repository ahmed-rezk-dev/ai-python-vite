from typing import Any, Dict, List, Optional, TypedDict

from fastapi import APIRouter

### Retrieval Grader
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama.llms import OllamaLLM
from langgraph.graph import END, START, StateGraph

router = APIRouter(prefix="/email", tags=["ai"])


model = OllamaLLM(model="llama3.1")


@router.get("")
def get():
    template = """Question: {question}

    Answer: Let's think step by step."""

    prompt = ChatPromptTemplate.from_template(template)

    chain = prompt | model

    chain.invoke({"question": "What is LangChain?"})

    return chain.invoke({"question": "What is LangChain?", "document": ""})


class EmailState(TypedDict):
    email: Dict[str, Any]
    is_spam: Optional[bool]
    spam_reason: Optional[str]
    email_category: Optional[str]
    email_draft: Optional[str]
    messages: List[Dict[str, Any]]


def read_email(state: EmailState):
    email = state["email"]
    print(f"Alfred is processing an email from {email['sender']} with subject: {email['subject']}")
    return {}


def classify_email(state: EmailState):
    email = state["email"]
    prompt = f"""
As Alfred the butler of Mr wayne and it's SECRET identity Batman, analyze this email and determine if it is spam or legitimate and should be brought to Mr wayne's attention.

Email:
From: {email["sender"]}
Subject: {email["subject"]}
Body: {email["body"]}

First, determine if this email is spam.
answer with SPAM or HAM if it's legitimate. Only return the answer
Answer :
    """

    messages = [HumanMessage(content=prompt)]
    response = model.invoke(messages)

    response_text = response.lower()
    # __AUTO_GENERATED_PRINT_VAR_START__
    print(f" response_text: {str(response_text)}")  # __AUTO_GENERATED_PRINT_VAR_END__
    is_spam = "spam" in response_text and "ham" not in response_text

    if not is_spam:
        new_message = state.get("messages", []) + [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response},
        ]
    else:
        new_message = state.get("messages", [])
        return {"is_spam": is_spam, "messages": new_message}


def handle_spam(state: EmailState):
    print("Alfred has marked the email as spam.")
    print("The email has been moved to the spam folder.")
    return {}


def drafting_response(state: EmailState):
    email = state["email"]

    prompt = f"""
As Alfred the butler, draft a polite preliminary response to this email.

Email:
From: {email["sender"]}
Subject: {email["subject"]}
Body: {email["body"]}

Draft a brief, professional response that Mr. Wayne can review and personalize before sending.
    """

    messages = [HumanMessage(content=prompt)]
    response = model.invoke(messages)

    new_messages = state.get("messages", []) + [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response},
    ]

    return {"email_draft": response, "messages": new_messages}


def notify_mr_wayne(state: EmailState):
    email = state["email"]

    print("\n" + "=" * 50)
    print(f"Sir, you've received an email from {email['sender']}.")
    print(f"Subject: {email['subject']}")
    print("\nI've prepared a draft response for your review:")
    print("-" * 50)
    print(state["email_draft"])
    print("=" * 50 + "\n")

    return {}


# Define routing logic
def route_email(state: EmailState) -> str:
    if state["is_spam"]:
        return "spam"
    else:
        return "legitimate"


# Define the graph
email_graph = StateGraph(EmailState)

# Add nodes
email_graph.add_node("read_email", read_email)  # the read_email node executes the read_mail function
email_graph.add_node("classify_email", classify_email)  # the classify_email node will execute the classify_email function
email_graph.add_node("handle_spam", handle_spam)  # same logic
email_graph.add_node("drafting_response", drafting_response)  # same logic
email_graph.add_node("notify_mr_wayne", notify_mr_wayne)  # same logic
