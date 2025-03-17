from openai import OpenAI
from voitta import VoittaRouter
from dotenv import load_dotenv
import os
import yaml
import asyncio
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

voittaRouter = VoittaRouter("config/voitta.yaml")

tools = voittaRouter.get_tools()

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Show me the files at /tmp"}],
    tools=tools
)

function_name = completion.choices[0].message.tool_calls[0].function.name
function_arguments = eval(
    completion.choices[0].message.tool_calls[0].function.arguments)

print(f"Function name: {function_name}")
print(f"Function arguments: {function_arguments}")

result = asyncio.run(voittaRouter.call_function(
    function_name, function_arguments, "", "", ""))
print(result)
