from openai import OpenAI
from voitta import VoittaRouter
from dotenv import load_dotenv
import os
import yaml
import asyncio
import json
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create a tool router that can handle more than 128 tools


def create_tool_router(all_tools):
    # Group tools by category
    tool_categories = {}
    for tool in all_tools:
        name = tool['function']['name']
        # Extract category from the name (e.g., "mcp____filesystem_X_read_file" -> "filesystem")
        parts = name.split('_X_')
        if len(parts) > 1:
            category = parts[0].split('____')[-1]
        else:
            category = "other"

        if category not in tool_categories:
            tool_categories[category] = []
        tool_categories[category].append(tool)

    # Create a list_categories tool
    list_categories_tool = {
        "type": "function",
        "function": {
            "name": "list_tool_categories",
            "description": "List all available tool categories",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }

    # Create a list_tools_in_category tool
    list_tools_in_category_tool = {
        "type": "function",
        "function": {
            "name": "list_tools_in_category",
            "description": "List all tools in a specific category",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "The category name"
                    }
                },
                "required": ["category"]
            }
        }
    }

    # Create a execute_tool tool
    execute_tool_tool = {
        "type": "function",
        "function": {
            "name": "execute_tool",
            "description": "Execute a specific tool by name with arguments",
            "parameters": {
                "type": "object",
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": "The full name of the tool to execute"
                    },
                    "arguments": {
                        "type": "object",
                        "description": "The arguments to pass to the tool"
                    }
                },
                "required": ["tool_name", "arguments"]
            }
        }
    }

    # Return the router tools and the tool map
    router_tools = [list_categories_tool,
                    list_tools_in_category_tool, execute_tool_tool]
    return router_tools, tool_categories, all_tools


async def main():
    # Initialize VoittaRouter with the configuration file
    voittaRouter = VoittaRouter("config/voitta.yaml")

    # Discover MCP tools asynchronously
    await voittaRouter.discover_mcp_tools()

    # Get all tools (including MCP tools)
    all_tools = voittaRouter.get_tools()

    # Print available tools for debugging
    print(f"Found {len(all_tools)} tools:")

    # Create the tool router
    router_tools, tool_categories, tool_map = create_tool_router(all_tools)
    print(f"Created router with {len(tool_categories)} categories")

    # First, let the model explore available categories
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You have access to many tools through a router system. First list categories, then list tools in relevant categories, then execute the appropriate tool."},
            {"role": "user", "content": "Show me the files at /tmp"}
        ],
        tools=router_tools
    )

    # Process the initial tool call
    message = completion.choices[0].message
    print(f"Model response: {message.content}")

    # Handle the conversation flow
    conversation_history = [
        {"role": "system", "content": "You have access to many tools through a router system. First list categories, then list tools in relevant categories, then execute the appropriate tool."},
        {"role": "user", "content": "Show me the files at /tmp"}
    ]

    if hasattr(message, 'tool_calls') and message.tool_calls:
        tool_call = message.tool_calls[0]
        function_name = tool_call.function.name
        function_arguments = json.loads(tool_call.function.arguments)

        print(f"Function called: {function_name}")
        print(f"Arguments: {function_arguments}")

        # Handle the tool call
        if function_name == "list_tool_categories":
            categories = list(tool_categories.keys())
            tool_result = f"Available categories: {', '.join(categories)}"
            print(f"Tool result: {tool_result}")

            # Add to conversation
            conversation_history.append(message.model_dump())
            conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": tool_result
            })

            # Continue the conversation
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=conversation_history,
                tools=router_tools
            )

            message = completion.choices[0].message
            print(f"Model response: {message.content}")

            # Process the next tool call if any
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_call = message.tool_calls[0]
                function_name = tool_call.function.name
                function_arguments = json.loads(tool_call.function.arguments)

                print(f"Function called: {function_name}")
                print(f"Arguments: {function_arguments}")

                # Handle the tool call
                if function_name == "list_tools_in_category":
                    category = function_arguments.get("category")
                    if category in tool_categories:
                        tools_in_category = [tool['function']['name']
                                             for tool in tool_categories[category]]
                        tool_result = f"Tools in category '{category}':\n" + "\n".join(
                            tools_in_category)
                    else:
                        tool_result = f"Category '{category}' not found"

                    print(f"Tool result: {tool_result}")

                    # Add to conversation
                    conversation_history.append(message.model_dump())
                    conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": tool_result
                    })

                    # Continue the conversation
                    completion = client.chat.completions.create(
                        model="gpt-4o",
                        messages=conversation_history,
                        tools=router_tools
                    )

                    message = completion.choices[0].message
                    print(f"Model response: {message.content}")

                    # Process the final tool call
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        tool_call = message.tool_calls[0]
                        function_name = tool_call.function.name
                        function_arguments = json.loads(
                            tool_call.function.arguments)

                        print(f"Function called: {function_name}")
                        print(f"Arguments: {function_arguments}")

                        if function_name == "execute_tool":
                            tool_name = function_arguments.get("tool_name")
                            arguments = function_arguments.get("arguments")

                            print(f"Executing tool: {tool_name}")
                            print(f"With arguments: {arguments}")

                            # Call the actual function
                            result = await voittaRouter.call_function(
                                tool_name, arguments, "", "", "")
                            print(f"Result: {result}")

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
