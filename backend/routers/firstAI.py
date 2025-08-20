import uuid
from typing import Optional
from fastapi import APIRouter, Cookie

from ollama import ChatResponse, Client
from IPython.display import display, Markdown
import json


router = APIRouter(prefix="/firstai", tags=["ai"])


def get_session_id(session_id: Optional[str] = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())


@router.get("/html", response_model=None)
def get():
    client = Client(
        host="http://192.168.50.252:11434", headers={"x-some-header": "some-value"}
    )

    friends_list = ["Tommy", "Isabel", "Daniel"]
    list_of_tasks = [
        "Compose a brief email to my boss explaining that I will be late for tomorrow's meeting.",
        "Write a birthday poem for Otto, celebrating his 28th birthday.",
        "Write a 300-word review of the movie 'The Arrival'.",
    ]

    ice_cream_flavors = ["Chocolate", "Mint Chocolate Chip"]

    food_preferences_tommy = {
        "dietary_restrictions": "vegetarian",
        "favorite_ingredients": ["tofu", "olives"],
        "experience_level": "intermediate",
        "maximum_spice_level": 6,
    }

    prompt = f"""Please suggest a rescipe taht tries to include the following ingredients: {food_preferences_tommy["favorite_ingredients"]}
    The recipe should adhere to the following dietary restrictions: {food_preferences_tommy["dietary_restrictions"]}
    The difficulty of the recipe should be: {food_preferences_tommy["experience_level"]}
    The maximum spice level on a scale of 10 should be: {food_preferences_tommy["maximum_spice_level"]}
    Provide a two sentence description
    """

    response: ChatResponse = client.chat(
        model="llama3:latest",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    # Reading Markdown
    file = open("./baking.md")
    recipe = file.read()
    file.close()

    recipePrompt = (
        f"""Please suggest different rescipe suing the following steps: {recipe} """
    )

    recipeResponse: ChatResponse = client.chat(
        model="llama3:latest",
        messages=[
            {
                "role": "user",
                "content": recipePrompt,
            },
        ],
    )
    return recipeResponse.message.content
