import base64
from typing import Annotated, TypedDict

from fastapi import APIRouter
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_ollama.chat_models import ChatOllama
from langchain_ollama.llms import OllamaLLM
from langfuse.langchain import CallbackHandler
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

text_llm = OllamaLLM(model="llama3.1")
vision_llm = OllamaLLM(model="gemma3:12b")

route = APIRouter(prefix="/analysis", tags=["ai"])


class AgentState(TypedDict):
    """Define Agent State."""

    input_file: str | None  # Contains file path (PDF/PNG)
    messages: Annotated[list[AnyMessage], add_messages]


def extract_text(img_path: str) -> str:
    """Extract text from an image file using a multimodal model.

    Master Wayne often leaves notes with his training regimen or meal plans.
    This allows me to properly analyze the contents.
    """
    all_text = ""
    try:
        # Read image and encode as base64
        with open(img_path, "rb") as image_file:
            image_bytes = image_file.read()
        image_base64 = base64.b64decode(image_bytes).decode("utf-8")

        # Prepare the prompt including the base64 image data
        message = [
            HumanMessage(
                content=[
                    {"type": "text", "text": ("Extract all the text from this image.Return only the extracted text, no explainations.")},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                ]
            )
        ]

        # Call the vision-capable model
        response = vision_llm.invoke(message)

        # Append extracted text
        all_text += response + "\n\n"

        return all_text.strip()
    except Exception as e:
        # A butler should handle errors gracefully
        # You can choose whether to raise or just return an empty string / error message
        error_msg = f"Error extracting text: {str(e)}"
        print(error_msg)
        return ""


def divide(a: int, b: int) -> float:
    """Divide a and b."""
    return a / b


# Equip the butler with tools
tools = [divide, extract_text]

llm = ChatOllama(model="llama3.1")
llm_with_tools = llm.bind_tools(tools)


def assistant(state: AgentState):
    """Main function to handle the agent's state and logic."""
    # System message
    textual_description_of_tool = """
        extract_text(img_path: str): str
            Extract text from an image file using a multimodal model.

            Args:
                img_path: A local image file path (strings).

            Return:
                A signle string containing the concatenated text extracted from reach image.
        divide(a: int, b: int) -> float:
            Divide a and b
    """

    image = state["input_file"]
    sys_msg = SystemMessage(
        content=f"You are a helpful butler named Alfred that serves Mr. Wayne and Batman. You can analyse documents and run computations with provided tools:\n{textual_description_of_tool} \n You have access to some optional images. Currently the loaded image is: {image}"
    )

    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])], "input_file": state["input_file"]}


@route.get("")
def get():
    """We define a tools node with our list of tools. The assistant node is just our model with bound tools. We create a graph with assistant and tools nodes.

    We add a tools_condition edge, which routes to End or to tools based on whether the assistant calls a tool.

    Now, we add one new step:

    We connect the tools node back to the assistant, forming a loop.

        After the assistant node executes, tools_condition checks if the model’s output is a tool call.
        If it is a tool call, the flow is directed to the tools node.
        The tools node connects back to assistant.
        This loop continues as long as the model decides to call tools.
        If the model response is not a tool call, the flow is directed to END, terminating the process.
    """
    # The graph
    builder = StateGraph(AgentState)

    # Define nodes: these do the work
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))

    # Define edges: these determine how the control flow moves
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
        # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
        tools_condition,
    )
    builder.add_edge("tools", "assistant")
    react_graph = builder.compile()

    langfuse_handler = CallbackHandler()

    messages = [HumanMessage(content="According to the note provided by Mr. Wayne in the provided images. What's the list of items I should buy for the dinner menu?")]
    messages = react_graph.invoke({"messages": messages, "input_file": "Batman_training_and_meals.png"}, config={"callbacks": [langfuse_handler]})

    # Show the messages
    for m in messages["messages"]:
        m.pretty_print()

    # Show the butler's thought process
    graph_img = react_graph.get_graph(xray=True).draw_mermaid_png()
    return base64.encodebytes(graph_img).decode("utf-8")
