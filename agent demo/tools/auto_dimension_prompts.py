import json
from typing import Dict

def build_dimension_prompt(view_data: Dict) -> str:
    """
    根据视图中的几何图元信息生成用于 LLM 推理的提示语。

    参数：
        view_data (Dict): 包含视图名称和实体列表的字典

    返回：
        str: 可供 LLM 使用的自然语言提示字符串
    """
    example_prompt = '''
你是一位工程图尺寸标注专家，擅长按照《机械制图 尺寸注法》（GB/T 14689）等国家标准进行尺寸标注。

我将提供一组从工程视图中提取的几何图元信息（包含直线、圆弧和圆），请你判断：
1. 哪些位置应进行尺寸标注；
2. 应采用何种类型的标注（linear线性、radial半径、diameter直径、angle角度、ordinate坐标、symmetry对称等）；
3. 应如何标注尺寸数值和文字；
4. 应将标注放置于何处；

请你将分析结果以 JSON 数组形式返回，每个元素为一个标注建议，格式如下：
[
  {
    "type": "linear",
    "points": [[10, 20], [100, 20]],
    "value": "90",
    "position": "above",
    "note": "直线水平距离"
  },
  {
    "type": "radial",
    "center": [50, 50],
    "radius": 20,
    "value": "R20",
    "position": "right-top",
    "note": "圆的半径"
  }
]

下面是来自视图的图元数据：
'''
    geometries_json = json.dumps(view_data)
    example_prompt += f"{geometries_json}请基于这些数据进行推理，返回你建议的标注方案。"

    return example_prompt


def build_linear_dimension_prompt(view_data: Dict) -> str:
    """
    根据视图中的几何图元信息生成用于 LLM 推理的提示语。

    参数：
        view_data (Dict): 包含视图名称和实体列表的字典

    返回：
        str: 可供 LLM 使用的自然语言提示字符串
    """
    example_prompt = '''
你是一位工程图尺寸标注专家，擅长按照《机械制图 尺寸注法》（GB/T 14689）等国家标准进行尺寸标注。

我将提供一组从工程视图中提取的几何图元信息（包含直线、圆弧和圆），请你判断：
1. 哪些位置应进行尺寸标注；
2. 应采用何种类型的标注（linear线性、radial半径、diameter直径、angle角度、ordinate坐标、symmetry对称等）；
3. 应如何标注尺寸数值和文字；
4. 应将标注放置于何处；

⚠️ 请确保：
- 标注满足完备性，能完整表达几何形状和关键尺寸，特别是几何形状的定位标注，例如圆心到边界线的距离等能通过线性标注清晰表达的。
- 不重复、不冗余，例如封闭轮廓不需重复标注
- 对称/阵列特征可使用对称尺寸或孔标注

请你根据分析结果调用工具“zw3d_lineardim”完成标注。

下面是来自视图的图元数据：
'''
    geometries_json = json.dumps(view_data)
    example_prompt += (f"{geometries_json}。"
                       f"请基于这些数据进行推理，返回你建议的标注方案。请检查是否已覆盖：形状尺寸、定位尺寸、对称标注、中心标注等，若有遗漏请补充。"
f"请一次创建全部的线性标注指令，指令格式严格按照工具调用的格式(TOOL_CALL的格式)")

    return example_prompt