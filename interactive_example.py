from openai import OpenAI
from voitta import VoittaRouter
from dotenv import load_dotenv
import json
import os
import yaml
import asyncio
import sys

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize VoittaRouter with the configuration file
voittaRouter = VoittaRouter("config/voitta.yaml")


def create_tool_router():
    """Create a simple tool router to handle the OpenAI tool limit"""
    # Create a list_available_tools tool
    list_tools_tool = {
        "type": "function",
        "function": {
            "name": "list_available_tools",
            "description": "List all available tools and their descriptions",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }

    # Create an execute_tool tool
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
                        "description": "The name of the tool to execute"
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

    # Return the router tools
    return [list_tools_tool, execute_tool_tool]


async def main():
    # Discover MCP tools asynchronously
    await voittaRouter.discover_mcp_tools()

    # Get all tools (including MCP tools)
    all_tools = voittaRouter.get_tools()
    print(f"Loaded {len(all_tools)} tools")

    # Create a simple tool router
    router_tools = create_tool_router()

    # Create dictionaries to store tool information
    tool_info = {}      # name -> description
    tool_schemas = {}   # name -> parameters schema

    for tool in all_tools:
        name = tool["function"]["name"]
        description = tool["function"]["description"]
        parameters = tool["function"].get("parameters", {})

        tool_info[name] = description
        tool_schemas[name] = parameters

    # Initialize conversation with system message
    messages = [
        {"role": "system", "content": """You are a helpful assistant with access to various tools through a simple router.

1. First use list_available_tools to see what tools are available.
2. When you need to use a tool, use execute_tool with the correct tool_name and all required arguments.
3. Make sure to provide all required parameters for the tool you're using.
4. If you're not sure what parameters a tool requires, you can check the tool's schema in the list_available_tools response.

Example of using execute_tool:
```
execute_tool(
  tool_name: "get_file_contents",
  arguments: {
    "owner": "username",
    "repo": "repository",
    "path": "README.md"
  }
)
```

Be precise and thorough when using tools, and make sure to provide all required parameters."""}
    ]

    print("\n=== Interactive Voitta Chat ===")
    print("Type 'exit' to quit the conversation")
    print("===========================\n")

    # Main conversation loop
    while True:
        # Get user input
        print("\nYou: ", end="")
        user_input = input().strip()

        # Check if user wants to exit
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nGoodbye!")
            break

        # Add user message to conversation history
        messages.append({"role": "user", "content": user_input})

        # Get model response with router tools
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=router_tools
        )

        # Get the response
        response = completion.choices[0].message

        # Add assistant message to conversation history
        messages.append(response.model_dump())

        # Check if the model wants to use a tool
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                function_name = tool_call.function.name
                function_arguments = json.loads(tool_call.function.arguments)

                print(
                    f"\nAssistant: I'll use the {function_name} tool to help with that.")

                # Handle the tool call based on the function name
                if function_name == "list_available_tools":
                    # Format the tool information into a readable string with parameter details
                    tool_list = []
                    for name, description in tool_info.items():
                        schema = tool_schemas.get(name, {})
                        required_params = schema.get("required", [])
                        properties = schema.get("properties", {})

                        # Create parameter info string
                        param_info = ""
                        if required_params:
                            param_info = "\n    Required parameters: "
                            param_details = []
                            for param in required_params:
                                param_desc = properties.get(
                                    param, {}).get("description", "")
                                param_details.append(f"{param} ({param_desc})")
                            param_info += ", ".join(param_details)

                        tool_list.append(
                            f"- {name}: {description}{param_info}")

                    result = "Available tools:\n" + "\n".join(tool_list)

                    # Add tool response to conversation history
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": result
                    })

                    print(
                        f"Tool result: Listed {len(tool_info)} available tools")

                elif function_name == "execute_tool":
                    tool_name = function_arguments.get("tool_name")
                    arguments = function_arguments.get("arguments", {})

                    try:
                        # Check if the tool exists
                        if tool_name not in tool_info:
                            error_message = f"Tool '{tool_name}' not found. Use list_available_tools to see available tools."
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": function_name,
                                "content": error_message
                            })
                            print(f"\nError: {error_message}")
                        else:
                            # Validate arguments against the tool's schema
                            schema = tool_schemas.get(tool_name, {})
                            required_params = schema.get("required", [])
                            missing_params = [
                                param for param in required_params if param not in arguments]

                            if missing_params:
                                error_message = f"Missing required parameters for {tool_name}: {', '.join(missing_params)}"
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": function_name,
                                    "content": error_message
                                })
                                print(f"\nError: {error_message}")
                            else:
                                # Log the tool call for debugging
                                print(
                                    f"Calling {tool_name} with arguments: {json.dumps(arguments)}")

                                # Call the function through VoittaRouter
                                result = await voittaRouter.call_function(
                                    tool_name, arguments, "", "", ""
                                )

                                # Add tool response to conversation history
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": function_name,
                                    "content": f"Tool executed: {tool_name}\nResult: {result}"
                                })

                                print(f"Tool result: {result}")
                    except Exception as e:
                        error_message = f"Error executing tool {tool_name}: {str(e)}"
                        print(f"\nError: {error_message}")

                        # Add error to conversation history
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": error_message
                        })

            # Get a follow-up response from the model after tool use
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )

            response = completion.choices[0].message
            messages.append(response.model_dump())

        # Display the assistant's response
        print(f"\nAssistant: {response.content}")

if __name__ == "__main__":
    asyncio.run(main())
