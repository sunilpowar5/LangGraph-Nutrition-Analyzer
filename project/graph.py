import os
import requests
from typing import Optional
from typing_extensions import TypedDict
from dotenv import load_dotenv

from google import genai
from google.genai import types as genai_types

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph, END

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

# Load env variables
load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID")
NUTRITIONIX_API_KEY = os.getenv("NUTRITIONIX_API_KEY")

# Clients
client = genai.Client(api_key=GEMINI_API_KEY)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=GEMINI_API_KEY)

# Memory (for conversational loop)
memory = MemorySaver()

# State schema
class CalorieState(TypedDict):
    image_bytes: Optional[bytes]
    mime: Optional[str]
    food_items: Optional[str]
    result: Optional[str]
    user_query: Optional[str]
    user_result: Optional[str]


# Nodes
def Identify_foods(state: CalorieState):
    """Identify food items from image using Gemini."""
    part = genai_types.Part.from_bytes(
        data=state["image_bytes"], mime_type=state["mime"]
    )
    prompt = """
                You are analyzing an image to identify food items. Follow these rules:
                1. List all visible food items clearly.
                - Specify quantity (e.g., 2 bananas, 1 slice of bread).
                - Mention size/type if relevant (e.g., medium apple, large orange).
                2. If the food items are unclear or partially visible, suggest the user upload a clearer image.
                3. If the image does not contain food, tell the user it is not a food image and ask them to upload a proper food image.
                4. Output format must be structured as follows:
                Food Items:
                - <food item 1> (<quantity>, <size/type>)
                - <food item 2> (<quantity>, <size/type>)
                ...
            """
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=[part, prompt]
    )
    foods = response.text
    return {"food_items": foods}


@tool(description="Fetch nutrition facts for a food item using Nutritionix API.")
def nutritionix_fetching(query: str) -> dict:
    headers = {
        "x-app-id": NUTRITIONIX_APP_ID,
        "x-app-key": NUTRITIONIX_API_KEY,
        "Content-Type": "application/json",
    }
    resp = requests.post(
        "https://trackapi.nutritionix.com/v2/natural/nutrients",
        headers=headers,
        json={"query": query},
    )
    if resp.status_code == 200:
        return resp.json()
    else:
        return {"error": resp.text}


# Agent for fetching calories
agent = create_react_agent(
    model=llm,
    tools=[nutritionix_fetching],
     prompt="""You are a nutrition assistant. Use the nutritionix_fetching tool to find calories 
             and proteins. Return only nutrition facts in a clear format, no extra explanations."""
)


def fetch_calories(state: CalorieState):
    """Fetch calories using Nutritionix via the agent."""
    food_query = state["food_items"]

    prompt = f"""For the following food items: {food_query}

                            1. Use the nutrition_fetch tool for each food item listed.
                            2. Extract calories and protein information from the results.
                            3. List each food item with its calories and protein.
                            4. Show the total calories and total protein at the end.
                            5. Use bullet points for each food item.
                            6. Do not include explanations or methods, only nutrition facts.
                        """

    response = agent.invoke({
        "messages": [("human",prompt)]
        })
    final_response = response["messages"][-1].content
    return {"result": final_response}

# Defining chatbot outside because, no need of creating new chatbot when graph invoke again and again
chatbot = create_react_agent(
        model=llm,
        tools=[],
        prompt="""You are a nutrition assistant. 
            Use the previous nutrition analysis to answer user queries. 
            If the user points out missing or incorrect food items, 
            recalculate only for those items and update the totals.
            you can provide answers to user query if they ask about the
            food or nutrition as you are a nutrition assistant."""
    )

def user_query_chatbot(state: CalorieState):
    """Handle follow-up user queries about the calorie results."""
    user_message = state.get("user_query")
    if not user_message:
        return {"user_result": state.get("result", "No result yet.")}

    response = chatbot.invoke({"messages": [("human", f"The current calorie result is: {state['result']}. {user_message}")]})
    final_response = response["messages"][-1].content
    return {"user_result": final_response}


# Graph
def create_calorie_graph():
    builder = StateGraph(CalorieState)

    # nodes
    builder.add_node("identify_foods", Identify_foods)
    builder.add_node("fetch_calories", fetch_calories)
    builder.add_node("user_query", user_query_chatbot)

    # Conditional entry point
    def start_branch(state: CalorieState) -> str:
        if state.get("image_bytes"):
            return "identify_foods"
        elif state.get("user_query"):
            return "user_query"
        else:
            return END

    builder.add_conditional_edges(
        START,
        start_branch,
        {
            "identify_foods": "identify_foods",
            "user_query": "user_query",
            END: END,
        },
    )

    # After identify_foods -> fetch_calories
    builder.add_edge("identify_foods", "fetch_calories")

    # Conditional after fetch_calories
    def after_fetch(state: CalorieState) -> bool:
        return bool(state.get("user_query"))

    builder.add_conditional_edges(
        "fetch_calories",
        after_fetch,
        {True: "user_query", False: END},
    )

    # user_query always ends
    builder.add_edge("user_query", END)

    return builder.compile(checkpointer=memory)


calorie_graph = create_calorie_graph()
