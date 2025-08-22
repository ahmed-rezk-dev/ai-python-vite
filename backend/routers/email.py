import json
import base64
from typing import Any, Dict, List, Optional, TypedDict

from fastapi import APIRouter, Response

### Retrieval Grader
from langchain_core.messages import HumanMessage
from langchain_ollama.llms import OllamaLLM
from langfuse.langchain import CallbackHandler
from langgraph.graph import END, START, StateGraph
from pydantic import Base64Bytes

router = APIRouter(prefix="/email", tags=["ai"])


model = OllamaLLM(model="llama3.1")


# @router.get("")
# def get():
#     template = """Question: {question}
#
#     Answer: Let's think step by step."""
#
#     prompt = ChatPromptTemplate.from_template(template)
#
#     chain = prompt | model
#
#     chain.invoke({"question": "What is LangChain?"})
#
#     return chain.invoke({"question": "What is LangChain?", "document": ""})


class EmailState(TypedDict):
    # The email being processed
    email: Dict[str, Any]  # Contains subject, sender, body, etc.

    # Category of the email (inquiry, complaint, etc.)
    email_category: Optional[str]

    # Reason why the email was marked as spam
    spam_reason: Optional[str]

    # Analysis and decisions
    is_spam: Optional[bool]

    # Response generation
    email_draft: Optional[str]

    # Processing metadata
    messages: List[Dict[str, Any]]  # Track conversation with LLM for analysis


def read_email(state: EmailState):
    """Alfred reads and logs the incoming email."""
    email = state["email"]
    print(f"Alfred is processing an email from {email['sender']} with subject: {email['subject']}")
    return {}


def classify_email(state: EmailState):
    """Alfred uses an LLM to determine if the email is spam or legitimate."""
    email = state["email"]

    # Prepare our prompt for the LLM
    prompt = f"""
    As Alfred the butler, analyze this email and determine if it is spam or legitimate.

    Email:
    From: {email["sender"]}
    Subject: {email["subject"]}
    Body: {email["body"]}

    First, determine if this email is spam. explain why.
    if it is legitimate, categorize it (inquiry, complaint, thank you etc.).
    answer with SPAM or HAM and the reason.
    Answer:
    Reason:
    """

    # Call the LLM
    messages = [HumanMessage(content=prompt)]
    response = model.invoke(messages)

    # Simple logic to parse the response (in a real app, you'd want more robust parsing)
    response_text = response.lower()
    is_spam = "spam" in response_text and "not spam" not in response_text

    # Extract a reason if it's spam
    spam_reason = None
    if is_spam and "reason:" in response_text:
        spam_reason = response_text.split("reason:")[1].strip()

    # Determine category if legitimate
    email_category = None
    if not is_spam:
        categories = ["inquiry", "complaint", "thank you", "request", "information"]
        for category in categories:
            if category in response_text:
                email_category = category
                break

    # Update messages for tracking
    new_message = state.get("messages", []) + [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response},
    ]

    # Return state updates
    return {"is_spam": is_spam, "messages": new_message, "spam_reason": spam_reason, "email_category": email_category}


def handle_spam(state: EmailState):
    """Alfred discards spam email with a note."""
    print(f"Alfred has marked the email as spam. Reason: {state['spam_reason']}")
    print("The email has been moved to the spam folder.")

    # We're done processing this email
    return {}


def drafting_response(state: EmailState):
    """Alfred drafts a preliminary response for legitimate emails."""
    email = state["email"]
    category = state["email_category"]

    prompt = f"""
    As Alfred the butler, draft a polite preliminary response to this email.

    Email:
    From: {email["sender"]}
    Subject: {email["subject"]}
    Body: {email["body"]}

    This email has been categorized as: {category}

    Draft a brief, professional response that Mr. Wayne can review and personalize before sending.
    """

    # Call the LLM
    messages = [HumanMessage(content=prompt)]
    response = model.invoke(messages)

    # Update messages for tracking
    new_messages = state.get("messages", []) + [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response},
    ]

    # Return state updates
    return {"email_draft": response, "messages": new_messages}


def notify_mr_wayne(state: EmailState):
    """Alfred notifies Mr. Hugg about the email and presents the draft response."""
    email = state["email"]

    print("\n" + "=" * 50)
    print(f"Sir, you've received an email from {email['sender']}.")
    print(f"Subject: {email['subject']}")
    print(f"Category: {state['email_category']}")
    print("\nI've prepared a draft response for your review:")
    print("-" * 50)
    print(state["email_draft"])
    print("=" * 50 + "\n")

    # We're done processing this email
    return {}


# Define routing logic
def route_email(state: EmailState) -> str:
    """Determine the next step based on spam classification."""
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


# START the edges
email_graph.add_edge(START, "read_email")  # After starting we go to the "read_email" node

# Add edges - defining the flow
email_graph.add_edge("read_email", "classify_email")  # after_reading we classify

# Add conditional branching from classify_email
email_graph.add_conditional_edges(
    "classify_email",  # after classify, we run the "route_email" function"
    route_email,
    {
        "spam": "handle_spam",  # if it return "Spam", we go the "handle_span" node
        "legitimate": "drafting_response",  # and if it's legitimate, we go to the "drafting response" node
    },
)

# Add final edges
email_graph.add_edge("handle_spam", END)  # after handling spam we always end
email_graph.add_edge("drafting_response", "notify_mr_wayne")
email_graph.add_edge("notify_mr_wayne", END)  # after notifyinf Me wayne, we can end  too

# Compile the graph
compiled_graph = email_graph.compile()


@router.get("")
def get():
    # Example legitimate email
    legitimate_email = {
        "sender": "john.smith@example.com",
        "subject": "Question about your services",
        "body": "Dear Mr. Hugg, I was referred to you by a colleague and I'm interested in learning more about your consulting services. Could we schedule a call next week? Best regards, John Smith",
    }

    # Example spam email
    spam_email = {
        "sender": "winner@lottery-intl.com",
        "subject": "YOU HAVE WON $5,000,000!!!",
        "body": "CONGRATULATIONS! You have been selected as the winner of our international lottery! To claim your $5,000,000 prize, please send us your bank details and a processing fee of $100.",
    }

    # Process the legitimate email
    print("\nProcessing legitimate email...")
    legitimate_result = compiled_graph.invoke({"email": legitimate_email, "is_spam": None, "spam_reason": None, "email_category": None, "email_draft": None, "messages": []})

    # Process the spam email
    print("\nProcessing spam email...")
    spam_result = compiled_graph.invoke({"email": spam_email, "is_spam": None, "spam_reason": None, "email_category": None, "email_draft": None, "messages": []})

    # Initialize Langfuse CallbackHandler for LangGraph/Langchain (tracing)
    langfuse_handler = CallbackHandler()

    # Process legitimate email
    print("\nProcessing legitimate email...")
    legitimate_result = compiled_graph.invoke(input={"email": legitimate_email, "is_spam": None, "draft_response": None, "messages": []}, config={"callbacks": [langfuse_handler]})

    # Process spam email
    print("\nProcessing spam email...")
    spam_result = compiled_graph.invoke(input={"email": spam_email, "is_spam": None, "draft_response": None, "messages": []}, config={"callbacks": [langfuse_handler]})

    graph_img = compiled_graph.get_graph().draw_mermaid_png()
    # __AUTO_GENERATED_PRINT_VAR_START__
    print(f"get GRAPH_IMG: {str(graph_img)}")  # __AUTO_GENERATED_PRINT_VAR_END__

    return base64.encodebytes(graph_img).decode("utf-8")
