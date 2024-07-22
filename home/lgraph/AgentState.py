from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages.utils import AnyMessage
from langchain_openai import ChatOpenAI

from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig

#from home.loaders.url import tools

final_tools = []

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            configuration = config.get("configurable", {})
            passenger_id = configuration.get("passenger_id", None)
            state = {**state, "user_info": passenger_id}
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}


# Haiku is faster and cheaper, but less accurate
# llm = ChatAnthropic(model="claude-3-haiku-20240307")
#llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=1)
llm = ChatOpenAI(temperature=0, model="gpt-4-0125-preview", streaming=True)
# You could swap LLMs, though you will likely want to update the prompts when
# doing so!
# from langchain_openai import ChatOpenAI

# llm = ChatOpenAI(model="gpt-4-turbo-preview")

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful customer support assistant for a Company. "
            " Use the provided tools to search for company policies, and other information to assist the user's queries. "
            " When searching, be persistent. Expand your query bounds if the first search returns no results. "
            " If a search comes up empty, expand your search before giving up."
            "\n\nCurrent user:\n\n{user_info}\n",
        ),
        ("placeholder", "{messages}"),
    ]
).partial()

def tool_set(tool):
    print("tools in Agent State",tool)
    for x in tool:
        final_tools.append(x)
    print("Final_Tool",final_tools)        

def assistant_set():
    print("Final tools while setting assistant is:",final_tools)
    part_1_assistant_runnable = primary_assistant_prompt | llm.bind_tools(final_tools)
    return part_1_assistant_runnable 