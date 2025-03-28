from .tool_base import Tool
import subprocess
import json
from typing import Dict, Any

class ZW3DCommandTool(Tool):
    """
    Tool for running ZW3D command.
    """
    @property
    def name(self) -> str:
        return "zw3d_command"

    @property
    def description(self) -> str:
        return "Execute a specific ZW3D remote command"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The name of the ZW3D command to execute",
                    },
                "params": {
                    "type": "object",
                    "description": "Parameters for the command in JSON format",
                    }
                },
            "required": ["command"]
        }

    def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:
                command: The ZW3D command to execute
                params: Parameters for the command in JSON format

        Returns:
            Dictionary containing command output, error message, and return code
        """
        command = input.get('command')
        params = input.get('params')

        json_str = json.dumps(params)

        cmd = [
            'zw3dremote',
            '-r', 'local',
            f'cmd=~{command}({json_str})'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }

