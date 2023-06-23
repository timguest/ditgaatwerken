from langchain.chat_models import ChatOpenAI
# human message represents message of the human, ai and chat to mimic the chatmessage.
from langchain.schema import HumanMessage, AIMessage, ChatMessage
# import some tools
from langchain.tools import format_tool_to_openai_function, YouTubeSearchTool, MoveFileTool
import os
import openai
from constants import OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

llm = ChatOpenAI(model="gpt-3.5-turbo-0613")

tools = [MoveFileTool()]
# put tool into a function schema
functions = [format_tool_to_openai_function(t) for t in tools]

message = llm.predict_messages([HumanMessage(content='move file foo to bar')], functions=functions)
print(message.additional_kwargs['function_call'])

print(functions)