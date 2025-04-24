import json
import os
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from .tool_base import Tool
from .GPTAgent import GPTAutoDimensionAgent

class GPTToolWrapper:
    """Wrapper to use tools with OpenAI GPT-4 models via function calling."""

    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tools = {}

    def _create_system_prompt(self) -> str:
        """Create a system prompt that explains available tools."""

        return f"""You are a helpful assistant with access to external tools. Use function calling to complete tasks.

                To use a tool, first explain your reasoning using Chain of Thought
                """

    def register_tool(self, tool: Tool):
        """Register a tool for GPT function calling."""
        self.tools[tool.name] = tool

    def _build_tool_specs(self):
        """Convert tool input_schema into OpenAI-compatible function definitions."""
        functions = []
        for name, tool in self.tools.items():
            functions.append({
                "name": name,
                "description": tool.description,
                "parameters": tool.input_schema
            })
        return functions

    def execute(self, user_input: str) -> str:
        messages = [
            {
                "role": "system",
                "content": self._create_system_prompt(),
            },
            {
                "role": "user",
                "content": user_input
            }
        ]

        response_content = ""

        functions = self._build_tool_specs()

        while True:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4.1-mini",  # 或 gpt-4o
                    messages=messages,
                    functions=functions,
                    function_call="auto"
                )

            except Exception as e:
                return f"Error detection: {str(e)}"

            message = response.choices[0].message
            messages.append(message)
            if message.content:
                response_content += message.content + "\n"

            if message.function_call:
                func_name = message.function_call.name
                args = json.loads(message.function_call.arguments)

                if func_name not in self.tools:
                    error = f"Tool '{func_name}' not registered."
                    messages.append({
                        "role": "function",
                        "name": func_name,
                        "content": error
                    })
                    continue

                try:
                    result = self.tools[func_name].run(args)
                    if result["return code"] == 1 and func_name == "zw3d_stdvucrt_dim":
                        print("need manual dimension.")
                        auto_dimension_agent = GPTAutoDimensionAgent(self.tools)
                        auto_dimension_result = auto_dimension_agent.generate_dimension_plan(result)
                        response_content += auto_dimension_result

                except Exception as e:
                    result = f"Error running tool '{func_name}': {e}"

                messages.append({
                    "role": "function",
                    "name": func_name,
                    "content": str(result)
                })
            else:
                return response_content or "<No response>"

