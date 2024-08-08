from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages.utils import AnyMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
# from loaders.url import lookup_policy
# from home.loaders.url import tools

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
            # "You are a grader assessing relevance of a retrieved document to a user question. \n "
            # "Here is the retrieved document: \n\n {context} \n\n"
            # "Here is the user question: {question} \n "
            "Use the provided tools to search for company policies and other information to assist the user's queries."
            "When searching, be persistent."    
            #"Expand your query bounds if the first search returns no results."
            #"If a search comes up empty, expand your search before giving up."
            "The only source of information is the documents provided,do not anwser on information other than provided."
            "Always ensure your responses remain relevant to the provided documents and company information."
            # "If a user's query is out of context or not covered by the provided documents, politely inform the user that you can only assist with questions related to the available information."
            # "\n\nCurrent user:\n\n{user_info}\n",
        ),
        ("placeholder", "{messages}"),
        # [
        #     ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
        # ]
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