from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from langfuse.langchain import CallbackHandler
import os

langfuse_handler = CallbackHandler()


class State(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

def chat_node(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

graph_builder = StateGraph(State)
graph_builder.add_node("chat_node", chat_node)
graph_builder.add_edge(START, "chat_node")
graph_builder.add_edge("chat_node", END)

def compile_graph_with_checkpointer(checkpointer):
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer

def main():
    DB_URI = "mongodb://admin:password123@mongodb:27017"
    config = {
        "configurable": {
            "thread_id": "1",
            "callbacks": [langfuse_handler]
        }
    }

    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)
        query = input("> ")
        result = graph_with_mongo.invoke(
            {"messages": [{"role": "user", "content": query}]}, config)
        print(result)

if __name__ == "__main__":
    main()