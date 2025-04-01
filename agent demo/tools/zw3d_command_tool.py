from sympy.strategies.core import switch

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


class ZW3DCommandOpen(Tool):
    """
    Tool for running ZW3D command.
    """
    @property
    def name(self) -> str:
        return "zw3d_open"

    @property
    def description(self) -> str:
        return "Execute ZW3D open command, open a specific file in ZW3D"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filePath": {
                    "type": "string",
                    "description": "file path to open",
                },
            },
            "required": ["filePath"]
        }

    def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:
                filePath: file path for the command to open in JSON format

        Returns:
            Dictionary containing command output, error message, and return code
        """
        params = input.get('filePath')

        json_str = {
            "filePath": f"{params}"
        }

        json_str = json.dumps(json_str)

        cmd = [
            'zw3dremote',
            '-r', 'local',
            f'cmd=~FILEOPEN({json_str})'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }


class ZW3DCommandExpPDF(Tool):
    """
    Tool for running ZW3D command.
    """
    @property
    def name(self) -> str:
        return "zw3d_expPdf"

    @property
    def description(self) -> str:
        return "Execute ZW3D export PDF command, export the active file into a PDF file"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "file path for export",
                },
                "pdfType": {
                    "type": "string",
                    "description": "export type",
                    "enum": ["RASTER", "VECTOR", "OBJECT"],
                    "default": "VECTOR"
                },
            },
            "required": ["path", "pdfType"]
        }

    def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:

        Returns:
            Dictionary containing command output, error message, and return code
        """
        path = input.get('path')
        pdfType = input.get('pdfType')
        if pdfType == "RASTER":
            pdfType = 0
        elif pdfType == "VECTOR":
            pdfType = 1
        else:
            pdfType = 2

        json_str = {
            "path": f"{path}",
            "pdfType": pdfType
        }

        json_str = json.dumps(json_str)

        cmd = [
            'zw3dremote',
            '-r', 'local',
            f'cmd=~EXPPDF({json_str})'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }

class ZW3DCommandCreateStdView(Tool):
    """
    Tool for running ZW3D command.
    """
    @property
    def name(self) -> str:
        return "zw3d_open"

    @property
    def description(self) -> str:
        return "Execute ZW3D open command, open a specific file in ZW3D"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "file path to insert",
                },
                "rootName":{
                    "type": "string",
                    "description": "root name"
                },
                "type":{
                    "type": "int",
                    "description": "standard view type"
                }
            },
            "required": ["path", "rootName", "type"]
        }

    def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:
                filePath: file path for the command to open in JSON format

        Returns:
            Dictionary containing command output, error message, and return code
        """
        path = input.get('path')
        rootName = input.get('rootName')
        viewType = input.get('type')

        json_str = {
            "path": f"{path}",
            "rootName": f"{rootName}",
            "type": viewType,
        }

        json_str = json.dumps(json_str)

        cmd = [
            'zw3dremote',
            '-r', 'local',
            f'cmd=~STDVU({json_str})'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }