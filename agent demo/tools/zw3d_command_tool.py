from .tool_base import Tool
import subprocess
import json
from typing import Dict, Any
from . import user_config

def CommandRun(cmd):
    return subprocess.run(cmd, cwd=user_config.app_path, capture_output=True, text=True, check=True, shell=True)

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

        result = CommandRun(cmd)
        
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

        result = CommandRun(cmd)
        print("result:", result)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }

class ZW3DCommandSave(Tool):
    """
    Tool for running ZW3D command.
    """
    @property
    def name(self) -> str:
        return "zw3d_save"

    @property
    def description(self) -> str:
        return "Execute ZW3D save command, save a specific file and may close it"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "close": {
                    "type": "integer",
                    "description": "whether close the file after save it. if user do not specify the value, default set to 0."
                                   "{close: 1, open: 0}",
                },
            },
            "required": []
        }

    def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:
                close: whether to close the file after saving it.

        Returns:
            Dictionary containing command output, error message, and return code
        """
        close = input.get('close')

        json_str = {
            "close": close
        }

        json_str = json.dumps(json_str)

        cmd = [
            'zw3dremote',
            '-r', 'local',
            f'cmd=~FILESAVE({json_str})'
        ]
        print(cmd)

        result = CommandRun(cmd)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }

class ZW3DCommandExp(Tool):
    """
    Tool for running ZW3D command for exporting.
    """
    @property
    def name(self) -> str:
        return "zw3d_exp"

    @property
    def description(self) -> str:
        return ("Execute ZW3D export command, export the active file into certain type's file. "
                "When the parameter 'type' is PDF or IMG, we need the parameter 'subtype', besides that 'subType' default to 0."
                "all parameters need to be set even if user do not specify the value")

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "file path for export.",
                },
                "type": {
                    "type": "integer",
                    "description": "export type list below:"
                                   "1 : IMG, 2: PDF, 3: GRP, 4: DWG, 5: IGES, 6: STEP, 7: JT, 8: PARA_TEXT, 9: PARA_BINARY,"
                                   "10: CAT5_PART, 11: CAT5_ASM, 12: HTML, 13: STL, 14: OBJ, 15: IDF_PART, 16: IDF_ASM.",
                },
                "subType": {
                    "type": "integer",
                    "description": "export subtype, only used for PDF or IMG, when user do not provide this parameter, set subType to 0.",
                }
            },
            "required": ["path", "type", "subType"]
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
        type = input.get('type')
        subType = input.get('subType')

        json_str = {
            "path": f"{path}",
            "type": type,
            "subType": subType
        }

        json_str = json.dumps(json_str)

        cmd = [
            'zw3dremote',
            '-r', 'local',
            f'cmd=~FILEEXPORT({json_str})'
        ]

        result = CommandRun(cmd)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }

class ZW3DCommandStdVuCreate(Tool):
    """
    Tool for running ZW3D command for creating a standard view on the active drawing.
    """
    @property
    def name(self) -> str:
        return "zw3d_stdvucrt"

    @property
    def description(self) -> str:
        return "Execute ZW3D standard view create command, project the standard view into the active drawing on specific location."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "file path for part need to be projected.",
                },
                "type": {
                    "type": "integer",
                    "description": "view type for standard view, if user do not specify the value, default set to 7"
                                   "{TOP: 1, FRONT: 2, RIGHT: 3, BACK: 4, BOTTOM: 5, LEFT: 6, ISOMETRIC: 7, DIMETRIC: 39}",
                },
                "x": {
                    "type": "number",
                    "description": "standard view location for x axis, if user do not specify the value, default set to 100.0",
                },
                "y": {
                    "type": "number",
                    "description": "standard view location for y axis, if user do not specify the value, default set to 100.0",
                }
            },
            "required": ["path", "type", "x", "y"]
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
        type = input.get('type')
        x = input.get('x')
        y = input.get('y')

        json_str = {
            "path": f"{path}",
            "type": type,
            "x": x,
            "y": y,
        }

        json_str = json.dumps(json_str)

        cmd = [
            'zw3dremote',
            '-r', 'local',
            f'cmd=~STDVUCRT({json_str})'
        ]

        result = CommandRun(cmd)
        
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }

class ZW3DCommandStdVuDim(Tool):
    """
    Tool for running ZW3D command for creating a standard view on the active drawing and add dimensions to the view.
    """
    @property
    def name(self) -> str:
        return "zw3d_stdvucrt_dim"

    @property
    def description(self) -> str:
        return ("Execute ZW3D standard view create command, project the standard view into the active drawing on specific location."
                "add dimension to the view")
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "file path for part need to be projected.",
                },
                "type": {
                    "type": "integer",
                    "description": "view type for standard view, if user do not specify the value, default set to 7"
                                   "{TOP: 1, FRONT: 2, RIGHT: 3, BACK: 4, BOTTOM: 5, LEFT: 6, ISOMETRIC: 7, DIMETRIC: 39}",
                },
                "x": {
                    "type": "number",
                    "description": "standard view location for x axis, if user do not specify the value, default set to 100.0",
                },
                "y": {
                    "type": "number",
                    "description": "standard view location for y axis, if user do not specify the value, default set to 100.0",
                }
            },
            "required": ["path", "type", "x", "y"]
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
        type = input.get('type')
        x = input.get('x')
        y = input.get('y')

        json_str = {
            "path": f"{path}",
            "type": type,
            "x": x,
            "y": y,
        }

        json_str = json.dumps(json_str)

        cmd = [
            'zw3dremote',
            '-r', 'local',
            f'cmd=~STDVUDIM({json_str})'
        ]

        result = CommandRun(cmd)

        # 调用 zw3dremote 后读取 JSON 文件
        return {
            "img_path": user_config.img_path,
            "done_path": user_config.done_path,
            "geom_data": user_config.json_file_path, ###json data
            "stderr": result.stderr.strip(),
            "return code": 1, ###return code 0: no error, 1: need response, <0: error
        }


class ZW3DCommandLinearDim(Tool):
    """
    Tool for running ZW3D command: dimension the line length.
    """
    @property
    def name(self) -> str:
        return "zw3d_lineardim"

    @property
    def description(self) -> str:
        return ("Execute ZW3D linear length dimension create command, for dimension the length of a line")

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "id" : {
                    "type": "integer",
                    "description": "line id, if user do not specify the value, default set to 0",
                },
                "start point": {
                    "type": "object",
                    "description": "start point for linear dimension, contain: 'x', 'y'.",
                    "properties": {
                        "x": {
                            "type": "number",
                            "description": "start point's x axis value."
                        },
                        "y": {
                            "type": "number",
                            "description": "start point's y axis value."
                        },
                    },
                    "required": ["x", "y"]
                },
                "end point": {
                    "type": "object",
                    "description": "end point for linear dimension, contain: 'x', 'y'.",
                    "properties": {
                        "x": {
                            "type": "number",
                            "description": "end point's x axis value."
                        },
                        "y": {
                            "type": "number",
                            "description": "end point's y axis value."
                        },
                    },
                    "required": ["x", "y"]
                },
                "text point": {
                    "type": "object",
                    "description": "text point for linear dimension, contain: 'x', 'y'.",
                    "properties": {
                        "x": {
                            "type": "number",
                            "description": "text point's x axis value."
                        },
                        "y": {
                            "type": "number",
                            "description": "text point's y axis value."
                        },
                    },
                    "required": ["x", "y"]
                },
            },
            "required": ["id", "start point", "end point", "text point"]
        }

    def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:

        Returns:
            Dictionary containing command output, error message, and return code
        """
        entId = input.get('id')
        start_point = input.get('start point')
        end_point = input.get('end point')
        text_point = input.get('text point')

        json_str = {
            "id": entId,
            "start point": start_point,
            "end point": end_point,
            "text point": text_point,
        }

        json_str = json.dumps(json_str)

        cmd = [
            'zw3dremote',
            '-r', 'local',
            f'cmd=~LINDIM({json_str})'
        ]

        result = CommandRun(cmd)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }

class ZW3DCommandLinearOffsetDim(Tool):
    """
    Tool for running ZW3D command: dimension the Parallel lines.
    """
    @property
    def name(self) -> str:
        return "zw3d_linearoffsetdim"

    @property
    def description(self) -> str:
        return ("Execute ZW3D distance dimension create command, for dimension the distance between two entities")

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "id1" : {
                    "type": "integer",
                    "description": "first entity's id",
                },
                "id2" : {
                    "type": "integer",
                    "description": "second entity's id",
                },
                "first point": {
                    "type": "object",
                    "description": "point on the first entity, attached by id1, contain: 'x', 'y'.",
                    "properties": {
                        "x": {
                            "type": "number",
                            "description": "first point's x axis value."
                        },
                        "y": {
                            "type": "number",
                            "description": "first point's y axis value."
                        },
                    },
                    "required": ["x", "y"]
                },
                "second point": {
                    "type": "object",
                    "description": "point on the second entity, attached by id2, contain: 'x', 'y'.",
                    "properties": {
                        "x": {
                            "type": "number",
                            "description": "second point's x axis value."
                        },
                        "y": {
                            "type": "number",
                            "description": "second point's y axis value."
                        },
                    },
                    "required": ["x", "y"]
                },
                "text point": {
                    "type": "object",
                    "description": "text point for linear offset dimension, contain: 'x', 'y'.",
                    "properties": {
                        "x": {
                            "type": "number",
                            "description": "text point's x axis value."
                        },
                        "y": {
                            "type": "number",
                            "description": "text point's y axis value."
                        },
                    },
                    "required": ["x", "y"]
                },
            },
            "required": ["type", "id1", "id2", "first point", "second point", "text point"]
        }

    def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:

        Returns:
            Dictionary containing command output, error message, and return code
        """
        id1 = input.get('id1')
        id2 = input.get('id2')
        fpoint = input.get('first point')
        spoint = input.get('second point')
        text_point = input.get('text point')

        json_str = {
            "id1": id1,
            "id2": id2,
            "first point": fpoint,
            "second point": spoint,
            "text point": text_point,
        }

        json_str = json.dumps(json_str)

        cmd = [
            'zw3dremote',
            '-r', 'local',
            f'cmd=~LINOFFSETDIM({json_str})'
        ]

        result = CommandRun(cmd)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }
    
class ZW3DCommandArcLengthDimensionTool(Tool):
    """
    Creates a arc length dimension base on an arc curve in drawing.
    """
    @property
    def name(self) -> str:
        return "zw3d_create_arc_length_dimension"

    @property
    def description(self) -> str:
        return """Creates a arc length dimension base on an arc curve in drawing
                  Require Inputs:
                      arc point:The point [x,y] on the arc that you want to add dimension.
                      arc id:the id of the curve that the arc point should attach to, 'attach' means the point will move with the curve.
                      text point:The point [x,y] to locate the first dimension text.
               """

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "arc point": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "The point [x,y] on the arc that you want to add dimension.",
                    },
                "arc id": {
                    "type": "integer",
                    "description": "the id of the curve that the arc point should attach to, 'attach' means the point will move with the curve.",
                    "default" : -1
                    },
                "text point":{
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "The point [x,y] to locate the first dimension text.",
                }
                },
            "required": ["command"]
        }

    def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a arc length Dimension.

        Args:
            input: Dictionary containing:
                arc point: The point [x,y] on the arc that you want to add dimension.
                arc id: the id of the curve that the arc point should attach to, 'attach' means the point will move with the curve.
                text point: The point [x,y] to locate the first dimension text.

        Returns:
            Dictionary containing error message and return code
        """

        command = 'ARCLENDIM'
        json_str = json.dumps(input)

        cmd = [
            'zw3dremote',
            '-r', 'local',
            f'~{command}({json_str})'
        ]
        
        result = CommandRun(cmd)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }
    
class ZW3DCommandRadialDimensionTool(Tool):
    """
    Creates a radial dimension base on an arc or circle in drawing.
    """
    @property
    def name(self) -> str:
        return "zw3d_create_radial_dimension"

    @property
    def description(self) -> str:
        return """Creates a radial dimension base on an arc or circle in drawing
                  Require Inputs:
                      point:The point [x,y] on the arc or circle that you want to add dimension.
                      id:the id of the curve that the point should attach to, 'attach' means the point will move with the curve.
                      text point:The point [x,y] to locate the first dimension text.
               """

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "point": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "The point [x,y] on the arc or circle that you want to add radial dimension.",
                    },
                "id": {
                    "type": "integer",
                    "description": "the id of the curve that the dimension point should attach to, 'attach' means the point will move with the curve.",
                    "default" : -1
                    },
                "text point":{
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "The point [x,y] to locate the first dimension text",
                }
                },
            "required": ["command"]
        }

    def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a radial Dimension.

        Args:
            input: Dictionary containing:
                point: The point [x,y] on the arc or circle that you want to add dimension.
                id: the id of the curve that the point should attach to, 'attach' means the point will move with the curve.
                text point: The point [x,y] to locate the first dimension text.

        Returns:
            Dictionary containing error message and return code
        """

        command = 'RADIALDIM'
        json_str = json.dumps(input)

        cmd = [
            'zw3dremote',
            '-r', 'local',
            f'~{command}({json_str})'
        ]
        
        result = CommandRun(cmd)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }

class ZW3DCommandHoleCalloutDimensionTool(Tool):
    """
    Creates a hole callout dimension base on an circle curve that is projected by a hole in drawing.
    """
    @property
    def name(self) -> str:
        return "zw3d_create_hole_callout_dimension"

    @property
    def description(self) -> str:
        return """Creates a hole callout dimension base on circle that is projected by a hole in drawing,
                  select a circle entity with its id, this tool will mark its information of quantities, radial, hole depth and so on.
                  Require Inputs:
                      hole curve id:the id of the circle curve that should be dimensioned.
                      view id:the id of the view that the circle belongs to.
                      text point:The point [x,y] to locate the first dimension text.
               """

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "hole curve id": {
                    "type": "integer",
                    "description": "the id of the circle curve that should be dimensioned.",
                    "default" : -1
                    },
                "view id": {
                    "type": "integer",
                    "description": "the id of the view that the circle belongs to.",
                    "default" : -1
                    },
                "text point":{
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "The point [x,y] to locate the first dimension text",
                }
                },
            "required": ["command"]
        }

    def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a hole callout Dimension.

        Args:
            input: Dictionary containing:
                hole curve id: the id of the circle curve that should be dimensioned.
                view id: the id of the view that the circle belongs to.
                text point: The point [x,y] to locate the first dimension text.

        Returns:
            Dictionary containing error message and return code
        """

        command = 'HOLECALLOUTDIM'
        json_str = json.dumps(input)

        cmd = [
            'zw3dremote',
            '-r', 'local',
            f'~{command}({json_str})'
        ]
        
        result = CommandRun(cmd)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }