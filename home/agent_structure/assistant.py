from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages.utils import AnyMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig

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

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Use the provided tools to search for company policies and other information to assist the user's queries."
            "The only source of information is the documents provided; do not answer with information other than what's provided."
            "Always ensure your responses remain relevant to the provided documents and company information."
        ),
        ("placeholder", "{messages}"),
    ]
).partial()

def tool_set(tool):
    print("tools in Agent State", tool)
    for x in tool:
        final_tools.append(x)
    print("Final_Tool", final_tools)

def assistant_set(temperature: float = 0.0):
    print("Final tools while setting assistant is:", final_tools)
    llm = ChatOpenAI(temperature=temperature, model="gpt-4-0125-preview", streaming=True)
    part_1_assistant_runnable = primary_assistant_prompt | llm.bind_tools(final_tools)
    return part_1_assistant_runnable
