from openai import OpenAI
from voitta import VoittaRouter
from dotenv import load_dotenv
import os
import yaml
import asyncio
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def main():
    # Initialize VoittaRouter with the configuration file
    voittaRouter = VoittaRouter("config/voitta.yaml")

    # Discover MCP tools asynchronously
    await voittaRouter.discover_mcp_tools()

    # Get all tools (including MCP tools)
    tools = voittaRouter.get_tools()

    # Print available tools for debugging
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(
            f"- {tool['function']['name']}: {tool['function']['description']}")

    # Create a completion with the tools
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Show me the files at /tmp"}],
        tools=tools
    )

    # Extract the function call information
    function_name = completion.choices[0].message.tool_calls[0].function.name
    function_arguments = eval(
        completion.choices[0].message.tool_calls[0].function.arguments)

    print(f"Function name: {function_name}")
    print(f"Function arguments: {function_arguments}")

    # Call the function
    result = await voittaRouter.call_function(
        function_name, function_arguments, "", "", "")
    print(result)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
