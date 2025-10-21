import blib2to3.pgen2.tokenize
from sympy.strategies.core import switch

from LLMWrappers.baseTool import Tool
import subprocess
import json
from typing import Dict, Any
import os, re
from pathlib import Path

exe = r"D:\ZW3D APIHW\Productionx64\ZW3dRemote.exe"
cwd = os.path.dirname(exe)

def _fix_zw3d_suffix(input_path: str) -> tuple[str, bool, str]:
    """
    规范化 ZW3D 模型路径：
    - 去除首尾空白与成对引号
    - 若为 Creo 版本化后缀（.prt.N / .asm.N），整段替换为 .Z3PRT / .Z3ASM
    - 若为常见“零件”后缀，替换为 .Z3PRT；若为“装配”后缀，替换为 .Z3ASM
    - 若无后缀，补 .Z3PRT
    - 其他未知后缀，保守替换为 .Z3PRT
    返回: (标准化后的路径, 是否发生修改, 修改原因)
    """
    if not input_path:
        return "", False, "empty"

    raw = input_path.strip().strip('"').strip("'")
    p = Path(raw)
    try:
        abs_p = p if p.is_absolute() else (Path.cwd() / p)
    except Exception:
        abs_p = p

    # 收集所有后缀，统一小写便于匹配，例如 ['.prt','.1']
    suffixes = [s.lower() for s in abs_p.suffixes]

    # 分类：哪些算“零件”后缀、哪些算“装配”后缀
    part_exts = {
        ".z3prt", ".prt", ".sldprt", ".catpart", ".ipt",  # 原生/各家“零件”
        ".stp", ".step", ".igs", ".iges", ".x_t", ".x_b", ".jt", ".stl", ".3mf"  # 交换/中性格式（默认按零件走）
    }
    asm_exts  = {".z3asm", ".asm", ".sldasm", ".catproduct", ".iam"}

    # 情况 1：Creo/ProE 版本化多段后缀（.prt.N / .asm.N）
    if len(suffixes) >= 2 and re.fullmatch(r"\.\d+", suffixes[-1]) and suffixes[-2] in (".prt", ".asm"):
        base_kind = suffixes[-2]
        target = ".Z3PRT" if base_kind == ".prt" else ".Z3ASM"
        # 去掉末尾两段后缀，然后加目标后缀
        new_name = abs_p.name
        for s in (suffixes[-1], suffixes[-2]):  # 注意先删最后一段，再删倒数第二段
            if new_name.lower().endswith(s):
                new_name = new_name[: -len(s)]
        new_name = new_name + target
        fixed = abs_p.with_name(new_name)
        changed = True
        reason = f"Creo 版本化后缀 {''.join(suffixes[-2:])} → {target}"

    else:
        # 情况 2：单段后缀或其他多段情况
        if not suffixes:
            # 无后缀，补 .Z3PRT
            fixed = abs_p.with_name(abs_p.name + ".Z3PRT")
            changed = True
            reason = "missing suffix → .Z3PRT"
        else:
            last = suffixes[-1]
            if last in (".z3prt", ".z3asm"):
                # 已是目标格式
                fixed = abs_p
                changed = False
                reason = "ok"
            elif last in part_exts:
                target = ".Z3PRT"
                # 仅替换最后一段后缀
                base = abs_p.name[:-len(last)] if abs_p.name.lower().endswith(last) else abs_p.stem
                fixed = abs_p.with_name(base + target)
                changed = True
                reason = f"{last} → {target}"
            elif last in asm_exts:
                target = ".Z3ASM"
                base = abs_p.name[:-len(last)] if abs_p.name.lower().endswith(last) else abs_p.stem
                fixed = abs_p.with_name(base + target)
                changed = True
                reason = f"{last} → {target}"
            else:
                # 未知后缀：保守按零件处理，替换所有后缀为 .Z3PRT
                # （避免像 .model.v1.2 这类多段被只替换最后一段）
                target = ".Z3PRT"
                new_name = abs_p.name
                for s in suffixes[::-1]:  # 从右往左删，确保顺序正确
                    if new_name.lower().endswith(s):
                        new_name = new_name[: -len(s)]
                fixed = abs_p.with_name(new_name + target)
                changed = True
                reason = f"unknown suffix {''.join(suffixes)} → {target}"

    # fixed_str = str(fixed).replace("\\", "/") if os.name == "nt" else str(fixed)
    fixed_str = str(fixed)
    return fixed_str, changed, reason


def CommandRun(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)

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
    def parameters(self) -> Dict[str, Any]:
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

    def run(self, command: str, params: str):
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:
                command: The ZW3D command to execute
                params: Parameters for the command in JSON format

        Returns:
            Dictionary containing command output, error message, and return code
        """
        cmd = [
            'zw3dremote',
            '-r', 'local',
            f'cmd=~{command}({params})'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

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
    def parameters(self) -> Dict[str, Any]:
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

    def run(self, filePath: str):
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:
                filePath: file path for the command to open in JSON format

        Returns:
            Dictionary containing command output, error message, and return code
        """
        path = f"{filePath}".replace("\\", "/")
        json_str = json.dumps({"filePath": path}, ensure_ascii=False, separators=(",", ":"))
        args = [exe, "-r", "127.0.0.1", f"cmd=~FILEOPEN({json_str})"]

        print("SENT:", args[-1])
        result = subprocess.run(args, capture_output=True, text=True, timeout=20, cwd=cwd)
        # print("rc=", result.returncode, "\nstdout:", result.stdout, "\nstderr:", result.stderr)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }

# class ZW3DCommandSave(Tool):
#     """
#     Tool for running ZW3D command.
#     """
#     @property
#     def name(self) -> str:
#         return "zw3d_save"
#
#     @property
#     def description(self) -> str:
#         return "Execute ZW3D save command, save a specific file and may close it"
#
#     @property
#     def parameters(self) -> Dict[str, Any]:
#         return {
#             "type": "object",
#             "properties": {
#                 "close": {
#                     "type": "integer",
#                     "description": "whether close the file after save it. if user do not specify the value, default set to 0."
#                                    "{close: 1, open: 0}",
#                 },
#             },
#             "required": []
#         }
#
#     def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Execute a ZW3D remote command.
#
#         Args:
#             input: Dictionary containing:
#                 close: whether to close the file after saving it.
#
#         Returns:
#             Dictionary containing command output, error message, and return code
#         """
#         try:
#             close = input.get('close')
#         except Exception as e:
#             return {
#                 "stdout": "",
#                 "stderr": "input parameters construction error",
#                 "return code": -1
#             }
#
#         json_str = {
#             "close": close
#         }
#
#         json_str = json.dumps(json_str)
#
#         cmd = [
#             'zw3dremote',
#             '-r', 'local',
#             f'cmd=~FILESAVE({json_str})'
#         ]
#         print(cmd)
#
#         result = subprocess.run(cmd, capture_output=True, text=True, check=True)
#
#         return {
#             "stdout": result.stdout.strip(),
#             "stderr": result.stderr.strip(),
#             "return code": result.returncode
#         }

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
    def parameters(self) -> Dict[str, Any]:
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

    def run(self, path:str, type:str, subType:str):
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:

        Returns:
            Dictionary containing command output, error message, and return code
        """
        path = f"{path}".replace("\\", "/")

        json_str = json.dumps({
            "path": f"{path}",
            "type": type,
            "subType": subType
        }, ensure_ascii=False, separators=(",", ":"))

        args = [exe, "-r", "127.0.0.1", f"cmd=~FILEEXPORT({json_str})"]

        print("SENT:", args[-1])
        result = subprocess.run(args, capture_output=True, text=True, timeout=20, cwd=cwd)
        # print("rc=", result.returncode, "\nstdout:", result.stdout, "\nstderr:", result.stderr)


        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }

# class ZW3DCommandStdVuCreate(Tool):
#     """
#     Tool for running ZW3D command for creating a standard view on the active drawing.
#     """
#     @property
#     def name(self) -> str:
#         return "zw3d_stdvucrt"
#
#     @property
#     def description(self) -> str:
#         return "Execute ZW3D standard view create command, project the standard view into the active drawing on specific location."
#
#     @property
#     def parameters(self) -> Dict[str, Any]:
#         return {
#             "type": "object",
#             "properties": {
#                 "path": {
#                     "type": "string",
#                     "description": "file path for part need to be projected.",
#                 },
#                 "type": {
#                     "type": "integer",
#                     "description": "view type for standard view, if user do not specify the value, default set to 7"
#                                    "{TOP: 1, FRONT: 2, RIGHT: 3, BACK: 4, BOTTOM: 5, LEFT: 6, ISOMETRIC: 7, DIMETRIC: 39}",
#                 },
#                 "x": {
#                     "type": "number",
#                     "description": "standard view location for x axis, if user do not specify the value, default set to 100.0",
#                 },
#                 "y": {
#                     "type": "number",
#                     "description": "standard view location for y axis, if user do not specify the value, default set to 100.0",
#                 }
#             },
#             "required": ["path", "type", "x", "y"]
#         }
#
#     def run(self, path:str, type:str, x:str, y:str):
#         """
#         Execute a ZW3D remote command.
#
#         Args:
#             input: Dictionary containing:
#
#         Returns:
#             Dictionary containing command output, error message, and return code
#         """
#         # try:
#         #     path = input.get('path')
#         #     type = input.get('type')
#         #     x = input.get('x')
#         #     y = input.get('y')
#         # except Exception as e:
#         #     return {
#         #         "stdout": "",
#         #         "stderr": "input parameters construction error",
#         #         "return code": -1
#         #     }
#
#         json_str = {
#             "path": f"{path}",
#             "type": type,
#             "x": x,
#             "y": y,
#         }
#
#         json_str = json.dumps(json_str)
#
#         cmd = [
#             'zw3dremote',
#             '-r', 'local',
#             f'cmd=~STDVUCREATE({json_str})'
#         ]
#
#         print(cmd)
#
#         result = subprocess.run(cmd, capture_output=True, text=True, check=True)
#
#         return {
#             "stdout": result.stdout.strip(),
#             "stderr": result.stderr.strip(),
#             "return code": result.returncode
#         }

class ZW3DCommandStdVuDim(Tool):
    """
    Tool for running ZW3D command for creating a standard view on the active drawing and dimension the Parallel lines.
    """
    @property
    def name(self) -> str:
        return "zw3d_stdvucrt_dim"

    @property
    def description(self) -> str:
        return ("Execute ZW3D standard view create command, project the standard view into the active drawing on specific location."
                "And auto dimension")
    @property
    def parameters(self) -> Dict[str, Any]:
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

    def run(self, path:str, type:str, x:str, y:str):
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:

        Returns:
            Dictionary containing command output, error message, and return code
        """
        # path = f"{path}".replace("\\", "/")
        fixed_path, changed, reason = _fix_zw3d_suffix(path)
        warn_msg = None
        if changed:
            warn_msg = f"[ZW3DCommandStdVuDim] 输入路径后缀已修正：{reason} | src='{path}' → dst='{fixed_path}'"
            print(warn_msg)

        json_str = json.dumps({
            "path": f"{fixed_path}",
            "type": type,
            "x": x,
            "y": y,
        }, ensure_ascii=False, separators=(",", ":"))

        args = [exe, "-r", "127.0.0.1", f"cmd=~STDVUDIM({json_str})"]

        print("SENT:", args[-1])
        result = subprocess.run(args, capture_output=True, text=True, timeout=20, cwd=cwd)
        # # print("rc=", result.returncode, "\nstdout:", result.stdout, "\nstderr:", result.stderr)

        # 调用 zw3dremote 后读取 JSON 文件
        json_file_path = "D:/AI_AUTODIM_DATA/stdvu_output.json"
        img_path = "D:/AI_AUTODIM_DATA/stdvu_output.png"
        done_path = "D:/AI_AUTODIM_DATA/stdvu_output.done"

        return self.ok({
            "img_path": img_path,
            "done_path": done_path,
            "geom_data": json_file_path, ###json data
            "stderr": result.stderr.strip(),
            "return code": 1, ###return code 0: no error, 1: need response, <0: error
            "message": "std view created; need auto-dimension.",
        })


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
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "id" : {
                    "type": "integer",
                    "description": "line id, if user do not specify the value, default set to 0",
                },
                "start_point": {
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
                "end_point": {
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
                "text_point": {
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
            "required": ["id", "start_point", "end_point", "text_point"]
        }

    def run(self, id:str, start_point:str, end_point:str, text_point:str):
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:

        Returns:
            Dictionary containing command output, error message, and return code
        """
        json_str = json.dumps({
            "id": id,
            "start point": start_point,
            "end point": end_point,
            "text point": text_point,
        }, ensure_ascii=False, separators=(",", ":"))

        args = [exe, "-r", "127.0.0.1", f"cmd=~LINDIM({json_str})"]

        print("SENT:", args[-1])
        result = subprocess.run(args, capture_output=True, text=True, timeout=20, cwd=cwd)
        # print("rc=", result.returncode, "\nstdout:", result.stdout, "\nstderr:", result.stderr)

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
    def parameters(self) -> Dict[str, Any]:
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
                "first_point": {
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
                "second_point": {
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
                "text_point": {
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
            "required": ["id1", "id2", "first_point", "second_point", "text_point"]
        }

    def run(self, id1:str, id2:str, first_point:str, second_point:str, text_point:str):
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:

        Returns:
            Dictionary containing command output, error message, and return code
        """
        json_str = json.dumps({
            "id1": id1,
            "id2": id2,
            "first point": first_point,
            "second point": second_point,
            "text point": text_point,
        }, ensure_ascii=False, separators=(",", ":"))

        args = [exe, "-r", "127.0.0.1", f"cmd=~LINOFFSETDIM({json_str})"]

        print("SENT:", args[-1])
        result = subprocess.run(args, capture_output=True, text=True, timeout=20, cwd=cwd)
        # print("rc=", result.returncode, "\nstdout:", result.stdout, "\nstderr:", result.stderr)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }


class ZW3DCommandArcLengthDimension(Tool):
    """
    Creates an arc length dimension base on an arc curve in drawing.
    """

    @property
    def name(self) -> str:
        return "zw3d_arclengthdim"

    @property
    def description(self) -> str:
        return ("Execute ZW3D arc length dimension create command to create a arc length dimension base on an arc curve in drawing")

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "arc_id": {
                    "type": "integer",
                    "description": "the id of the curve that the arc point should attach to, 'attach' means the point will move with the curve.",
                    "default": -1
                },
                "arc_point": {
                    "type": "object",
                    "description": "point on the arc, attached by arc id, contain: 'x', 'y'.",
                    "properties": {
                        "x": {
                            "type": "number",
                            "description": "arc point's x axis value."
                        },
                        "y": {
                            "type": "number",
                            "description": "arc point's y axis value."
                        },
                    },
                    "required": ["x", "y"]
                },
                "text_point": {
                    "type": "object",
                    "description": "text point for arc length dimension, contain: 'x', 'y'.",
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
            "required": ["arc_id", "arc_point", "text_point"]
        }

    def run(self, arc_id:str, arc_point:str, text_point:str):
        """
        Create an arc length Dimension.

        Args:
            input: Dictionary containing:
                arc point: The point {x,y} on the arc that you want to add dimension.
                arc id: the id of the curve that the arc point should attach to, 'attach' means the point will move with the curve.
                text point: The point {x,y} to locate the first dimension text.

        Returns:
            Dictionary containing error message and return code
        """
        command = 'ARCLENDIM'
        json_str = json.dumps({
            "arc id": arc_id,
            "arc point": arc_point,
            "text point": text_point,
        }, ensure_ascii=False, separators=(",", ":"))

        args = [exe, "-r", "127.0.0.1", f"cmd=~{command}({json_str})"]

        print("SENT:", args[-1])
        result = subprocess.run(args, capture_output=True, text=True, timeout=20, cwd=cwd)
        # print("rc=", result.returncode, "\nstdout:", result.stdout, "\nstderr:", result.stderr)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }


class ZW3DCommandRadialDimension(Tool):
    """
    Creates a radial dimension base on an arc or circle in drawing.
    """

    @property
    def name(self) -> str:
        return "zw3d_radialdim"

    @property
    def description(self) -> str:
        return ("Execute ZW3D radial dimension create command to Creates a radial dimension base on an arc or circle in drawing")

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer",
                    "description": "the id of the curve that the dimension point should attach to, 'attach' means the point will move with the curve.",
                    "default": -1
                },
                "point": {
                    "type": "object",
                    "description": "point on the arc or circle, attached by id, contain: 'x', 'y'.",
                    "properties": {
                        "x": {
                            "type": "number",
                            "description": "point's x axis value."
                        },
                        "y": {
                            "type": "number",
                            "description": "point's y axis value."
                        },
                    },
                },
                "text_point": {
                    "type": "object",
                    "description": "text point for radical dimension, contain: 'x', 'y'.",
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
            "required": ["id", "point", "text_point"]
        }

    def run(self, id:str, point:str, text_point:str) -> Dict[str, Any]:
        """
        Create a radial Dimension.

        Args:
            input: Dictionary containing:
                point: The point {x,y} on the arc or circle that you want to add dimension.
                id: the id of the curve that the point should attach to, 'attach' means the point will move with the curve.
                text point: The point {x,y} to locate the first dimension text.

        Returns:
            Dictionary containing error message and return code
        """

        command = 'RADIALDIM'
        json_str = json.dumps({
            "id": id,
            "point": point,
            "text point": text_point,
        }, ensure_ascii=False, separators=(",", ":"))

        args = [exe, "-r", "127.0.0.1", f"cmd=~{command}({json_str})"]

        print("SENT:", args[-1])
        result = subprocess.run(args, capture_output=True, text=True, timeout=20, cwd=cwd)
        # print("rc=", result.returncode, "\nstdout:", result.stdout, "\nstderr:", result.stderr)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }


class ZW3DCommandHoleCalloutDimension(Tool):
    """
    Creates a hole callout dimension base on an circle curve that is projected by a hole in drawing.
    """

    @property
    def name(self) -> str:
        return "zw3d_holecalloutdim"

    @property
    def description(self) -> str:
        return ("Execute ZW3D hole callout dimension create command to Creates a hole dimension base on circle that is projected by a hole in drawing, "
                  "select a circle entity with its id, this tool will mark its information of quantities, radial, hole depth and so on.")

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "hole_curve_id": {
                    "type": "integer",
                    "description": "the id of the circle curve that should be dimensioned.",
                    "default": -1
                },
                "view_id": {
                    "type": "integer",
                    "description": "the id of the view that the circle belongs to.",
                    "default": -1
                },
                "text_point": {
                    "type": "object",
                    "description": "text point for arc length dimension, contain: 'x', 'y'.",
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
            "required": ["hole_curve_id", "view_id", "text_point"]
        }

    def run(self, hole_curve_id:str, view_id:str, text_point:str):
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
        json_str = json.dumps({
            "hole curve id": hole_curve_id,
            "view id": view_id,
            "text point": text_point,
        }, ensure_ascii=False, separators=(",", ":"))

        args = [exe, "-r", "127.0.0.1", f"cmd=~{command}({json_str})"]

        print("SENT:", args[-1])
        result = subprocess.run(args, capture_output=True, text=True, timeout=20, cwd=cwd)
        # print("rc=", result.returncode, "\nstdout:", result.stdout, "\nstderr:", result.stderr)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }


class ZW3DCommandAsmTree(Tool):
    """
    Tool for running ZW3D command.
    """
    @property
    def name(self) -> str:
        return "zw3d_asmtree"

    @property
    def description(self) -> str:
        return ("Creates a multi-level assembly structure in ZW3D. Given a template part file (.Z3PRT), a target depth,"
                " and a total number of instances, this tool automatically generates a hierarchy of nested assemblies. "
                "Each level contains one assembly file, into which several component instances are randomly inserted. "
                "The insertion continues until the specified total number of components is reached. "
                "Finally, all generated assemblies are inserted into a top-level root assembly (root.Z3ASM).")

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "partPath": {
                    "type": "string",
                    "description": "The file path of the source part (.Z3PRT) to be inserted into the assembly, e.g., 'C:/model/part.Z3PRT'."
                },
                "saveDir": {
                    "type": "string",
                    "description": "The target directory where all generated .Z3ASM files will be saved, e.g., 'C:/output/'."
                },
                "depth": {
                    "type": "integer",
                    "description": "The number of nested levels of assemblies. For example, depth = 3 will create 3 intermediate assemblies plus a root."
                },
                "totalInstances": {
                    "type": "integer",
                    "description": "The total number of part instances to be inserted across all levels. These will be randomly distributed among intermediate assemblies."
                }
            },
            "required": ["partPath", "saveDir", "depth", "totalInstances"]
        }


    def run(self, partPath:str, saveDir:str, depth:str, totalInstances:str):
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:
                partPath: inserting part's path
                saveDir: save directory
                depth: the depth of the assembly
                totalInstances: the number of parts needed to be inserted

        Returns:
            Dictionary containing command output, error message, and return code
        """
        partPath = f"{partPath}".replace("\\", "/")
        saveDir = f"{saveDir}".replace("\\", "/")

        json_str = json.dumps({
            "partPath": partPath,
            "saveDir": saveDir,
            "depth": depth,
            "totalInstances": totalInstances,
        }, ensure_ascii=False, separators=(",", ":"))

        args = [exe, "-r", "127.0.0.1", f"cmd=~ASMTREE({json_str})"]

        print("SENT:", args[-1])
        result = subprocess.run(args, capture_output=True, text=True, timeout=20, cwd=cwd)
        # print("rc=", result.returncode, "\nstdout:", result.stdout, "\nstderr:", result.stderr)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }


class ZW3DCommandInsertComp(Tool):
    """
    Tool for running ZW3D command.
    """
    @property
    def name(self) -> str:
        return "zw3d_insertcomp"

    @property
    def description(self) -> str:
        return ("Inserts a part or sub-assembly into the currently active assembly. "
                "The user must provide the path to the component (.Z3PRT or .Z3ASM), "
                "and optionally a placement matrix (frame). If frame is omitted, the default location is used.")

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Absolute file path of the component to insert (.Z3PRT or .Z3ASM)."
                        },
                        "frame": {
                            "type": "array",
                            "description": "Optional 3x4 placement matrix as a flat array (length 12): [xx, yx, zx, xt, xy, yy, zy, yt, xz, yz, zz, zt].",
                            "items": { "type": "number" },
                            "minItems": 12,
                            "maxItems": 12
                        }
                    },
                    "required": ["path"]
                }


    def run(self, path:str, frame:str):
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:

        Returns:
            Dictionary containing command output, error message, and return code
        """
        path = f"{path}".replace("\\", "/")

        json_str = json.dumps({
            "path": path,
            "frame": frame,
        }, ensure_ascii=False, separators=(",", ":"))

        args = [exe, "-r", "127.0.0.1", f"cmd=~COMPINSERT({json_str})"]

        print("SENT:", args[-1])
        result = subprocess.run(args, capture_output=True, text=True, timeout=20, cwd=cwd)
        # print("rc=", result.returncode, "\nstdout:", result.stdout, "\nstderr:", result.stderr)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }


class ZW3DCommandNewFile(Tool):
    """
    Tool for running ZW3D command.
    """
    @property
    def name(self) -> str:
        return "zw3d_newfile"

    @property
    def description(self) -> str:
        return ("Create a specified file on the path")

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
                    "type": "object",
                    "properties": {
                        "savePath": {
                            "type": "string",
                            "description": "Absolute file path and file name of the specified file."
                        },
                    },
                    "required": ["savePath"]
                }


    def run(self, savePath:str):
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:

        Returns:
            Dictionary containing command output, error message, and return code
        """
        savePath = f"{savePath}".replace("\\", "/")

        json_str = json.dumps({
            "savePath": savePath,
        }, ensure_ascii=False, separators=(",", ":"))

        args = [exe, "-r", "127.0.0.1", f"cmd=~FILENEW({json_str})"]

        print("SENT:", args[-1])
        result = subprocess.run(args, capture_output=True, text=True, timeout=20, cwd=cwd)
        # print("rc=", result.returncode, "\nstdout:", result.stdout, "\nstderr:", result.stderr)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }


class ZW3DCommandActiveFile(Tool):
    """
    Tool for running ZW3D command.
    """
    @property
    def name(self) -> str:
        return "zw3d_activefile"

    @property
    def description(self) -> str:
        return ("Activate the specified file(.Z3PRT or .Z3ASM)")

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
                    "type": "object",
                    "properties": {
                        "filePath": {
                            "type": "string",
                            "description": "Absolute file path and file name of the specified file."
                        },
                    },
                    "required": ["filePath"]
                }


    def run(self, filePath:str):
        """
        Execute a ZW3D remote command.

        Args:
            input: Dictionary containing:

        Returns:
            Dictionary containing command output, error message, and return code
        """
        filePath = f"{filePath}".replace("\\", "/")

        json_str = json.dumps({
            "filePath": filePath,
        }, ensure_ascii=False, separators=(",", ":"))

        args = [exe, "-r", "127.0.0.1", f"cmd=~FILEACTIVE({json_str})"]

        print("SENT:", args[-1])
        result = subprocess.run(args, capture_output=True, text=True, timeout=20, cwd=cwd)
        # print("rc=", result.returncode, "\nstdout:", result.stdout, "\nstderr:", result.stderr)

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return code": result.returncode
        }
