import json
import os
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from .tool_base import Tool
from tools.tool_decorator import auto_fallback_if_incomplete

class DeepseekToolWrapper:
    """Wrapper to use tools with Deepseek Reasoner through prompt engineering."""
    
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        self.tools = {}
        
    def _convert_schema_to_nl(self, schema: Dict) -> str:
        """Convert JSONSchema to natural language description."""
        nl_desc = []
        for name, details in schema.get("properties", {}).items():
            desc = details.get("description", "No description available")
            type_info = details.get("type", "any")
            required = name in schema.get("required", [])
            nl_desc.append(f"- {name} ({type_info}{'*' if required else ''}): {desc}")
        return "\n".join(nl_desc)
        
    def register_tool(self, tool: Tool):
        """Register a tool with a natural language description."""
        self.tools[tool.name] = {
            "tool": tool,
            "description": tool.description,
            "schema": self._convert_schema_to_nl(tool.input_schema)
        }
    
    def _create_system_prompt(self) -> str:
        """Create a system prompt that explains available tools."""
        tools_desc = ""
        for name, info in self.tools.items():
            tools_desc += f"\nTool: {name}\n"
            tools_desc += f"Description: {info['description']}\n"
            tools_desc += f"Input_schema:\n{info['schema']}\n"
            
        return f"""You are an AI assistant with access to the following tools:
{tools_desc}

To use a tool, first explain your reasoning using Chain of Thought, then respond with a tool call in this EXACT format:
TOOL_CALL:
{{
    "tool": "tool_name",
    "input_schema": {{
        "param1": "value1",
        "param2": "value2"
    }}
}}

Make sure to:
1. Use valid JSON format
2. Include all required input_schema
3. Use correct parameter types
4. Only use tools that are listed above"""

    # def _extract_tool_call(self, content: str) -> Optional[Dict[str, Any]]:
    #     """Extract and parse tool call from model response."""
    #     try:
    #         if "TOOL_CALL:" not in content:
    #             return None
    #
    #         tool_json = content.split("TOOL_CALL:")[1].strip()
    #         return json.loads(tool_json)
    #     except Exception as e:
    #         print(f"Error parsing tool call: {e}")
    #         return None

    def _extract_tool_calls(self, content: str) -> list[Dict[str, Any]]:
        """从模型响应中提取所有 TOOL_CALL JSON 块。"""
        calls = []
        try:
            parts = content.split("TOOL_CALL:")
            for part in parts[1:]:
                try:
                    json_candidate = part.strip().split("\n\n")[0].strip()
                    calls.append(json.loads(json_candidate))
                except Exception as e:
                    print(f"Warning: Failed to parse one tool call: {e}")
        except Exception as e:
            print(f"Error parsing tool calls: {e}")
        return calls

    # def execute(self, user_input: str) -> str:
    #     """Execute a tool based on user input."""
    #     try:
    #         # Get model's response
    #         response = self.client.chat.completions.create(
    #             model="deepseek-reasoner",
    #             messages=[
    #                 {"role": "system", "content": self._create_system_prompt()},
    #                 {"role": "user", "content": user_input}
    #             ]
    #         )
    #
    #         # Get reasoning and potential tool call
    #         reasoning = response.choices[0].message.reasoning_content
    #         tool_call = self._extract_tool_call(response.choices[0].message.content)
    #
    #         if not tool_call:
    #             return f"Reasoning:\n{reasoning}\n\nNo valid tool call was made."
    #
    #         # Validate tool exists
    #         if tool_call["tool"] not in self.tools:
    #             return f"Reasoning:\n{reasoning}\n\nError: Tool '{tool_call['tool']}' not found."
    #
    #         # Execute tool
    #         result = self.tools[tool_call["tool"]]["tool"].run(tool_call["input_schema"])
    #
    #         return f"Reasoning:\n{reasoning}\n\nTool Call:\n{json.dumps(tool_call, indent=2)}\n\nResult:\n{result}"
    #
    #     except Exception as e:
    #         return f"Error executing tool: {str(e)}"

    def execute_multi_step(self, user_input: str, max_steps: int = 5,
                           skip_first: Optional[Dict[str, Any]] = None) -> str:
        messages = [
            {"role": "system", "content": self._create_system_prompt()},
            {"role": "user", "content": user_input}
        ]
        all_reasoning = []
        all_results = []

        for step in range(max_steps):
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=messages
            )
            message = response.choices[0].message
            reasoning = getattr(message, "reasoning_content", "")
            content = message.content

            all_reasoning.append(f"Step {step + 1} Reasoning:\n{reasoning}")
            tool_calls = self._extract_tool_calls(content)
            if not tool_calls:
                all_results.append(f"Step {step + 1}: No TOOL_CALL found. Halting.")
                break

            for tool_call in tool_calls:
                if skip_first and tool_call == skip_first:
                    print("[Skip] 跳过已执行的第一条工具调用")
                    skip_first = None
                    continue

                tool_name = tool_call.get("tool")
                input_schema = tool_call.get("input_schema", {})

                if tool_name not in self.tools:
                    result = f"Error: Tool '{tool_name}' not registered."
                else:
                    try:
                        result = self.tools[tool_name]["tool"].run(input_schema)
                    except Exception as e:
                        result = f"Error executing tool '{tool_name}': {e}"

                # 用自然语言方式反馈结果（无 role="tool"）
                messages.append({
                    "role": "assistant",
                    "content": f"TOOL_CALL:\n{json.dumps(tool_call)}\n\nResult:\n{json.dumps(result)}"
                })

                messages.append({
                    "role": "user",
                    "content": "请继续完成后续操作。"
                })

                all_results.append(
                    f"Step {step + 1} Tool Call:\n{json.dumps(tool_call, indent=2)}\nResult:\n{result}"
                )

        return "\n\n".join(all_reasoning + all_results)

    @auto_fallback_if_incomplete("execute_multi_step")
    def execute(self, user_input: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": self._create_system_prompt()},
                    {"role": "user", "content": user_input}
                ]
            )
            reasoning = response.choices[0].message.reasoning_content
            content = response.choices[0].message.content
            tool_calls = self._extract_tool_calls(content)

            if not tool_calls:
                return f"{reasoning}\n指令已执行完成，还有什么可以帮你的吗？"
                # return f"{reasoning}\n\nNo valid tool call was made."

            return_str = f"{reasoning}\n指令已执行完成，还有什么可以帮你的吗？"
            for tool_call in tool_calls:
                tool_name = tool_call.get("tool")
                if tool_name not in self.tools:
                    return f"{reasoning}\n\nTool '{tool_name}' not found."

                result = self.tools[tool_name]["tool"].run(tool_call["input_schema"])

                # 缓存下第一条调用用于 fallback
                self._tool_count = len(tool_calls)
                self._last_tool_call = tool_call

                # return_str += f"TOOL_CALL:\n{json.dumps(tool_call, indent=2)}\n\nResult:\n{result}\n"

            return return_str

        except Exception as e:
            return f"Error executing tool: {str(e)}"




