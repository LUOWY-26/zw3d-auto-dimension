import openai, base64, json
from dotenv import load_dotenv
import os
import re

example_prompt = '''
You are an expert in mechanical drawing dimensioning, well-versed in applying the Chinese national standard GB/T 14689 (Mechanical Drawing - Dimensioning Rules).

Given an engineering drawing image and a set of geometric entities extracted from a 2D projection view (including lines, arcs, and circles), your task is to first associate the image with the corresponding geometry data. Each entity contains a unique ID and a set of key point coordinates.

Then, based on the geometry, please determine:
1. Which locations should be dimensioned;
2. What type of dimensions should be used (e.g., linear length, distance, radial, diameter, angle, ordinate, symmetry);
3. How to annotate the dimension values and labels;
4. Where to place the dimensions to avoid overlaps or occlusions between annotations.

Please ensure the following:
1. Make sure all referenced IDs actually exist in the provided geometry data. Do not fabricate IDs.
2. There is no need to label radius/diameter.
3. Every key entity(especially the holes) contributing to the geometry description must be dimensioned either directly or indirectly. Entities not involved in any dimension are considered potentially under-dimensioned unless they are auxiliary or redundant by symmetry.
4. Make sure to add locating dimensions for internal features (such as holes, slots, inner rectangles, etc.) relative to external edges, axes, or reference geometries. Every internal geometry must have clearly defined positioning dimensions to describe its relation to the main body.
Do not omit center-to-edge, center-to-center, or edge-to-edge distances that define the internal feature locations.
If an internal feature is symmetric, you may use symmetry dimensions. If it's a hole, use center-to-edge distances.
This is crucial for manufacturing and dimension completeness.

First, list each entity (including the ID) and the dimension associated with the entity, and output it into a list in JSON format. 
At the same time, list all entity IDs that are not associated with the label, and explain why these entities do not need to be labeled.

example:
已标注主要实体及其标注类型：
```json
[
  {"id":268, "type":"linear", "desc":"外轮廓底边长度（宽度）"},
  {"id":71,  "type":"linear", "desc":"外轮廓右侧竖边长度（高度）"},
  {"id":100, "type":"linear", "desc":"右侧辅助边（高度）"},
  {"id":422, "type":"linearoffset", "desc":"上下中心孔（圆心）间距"},
  {"id":422, "type":"linearoffset", "desc":"上孔中心到右侧基准边距离"},
  {"id":450, "type":"linearoffset", "desc":"内槽上水平长度1"},
  {"id":464, "type":"linearoffset", "desc":"内槽上水平长度2"},
  {"id":492, "type":"linearoffset", "desc":"内槽左侧竖直高度"},
  {"id":578, "type":"linearoffset", "desc":"内槽槽口与外壳定位距离"}
]
```

未参与直接标注的实体及理由：
- 大量圆弧（如86,128,198,226,282,310,338,352,380,408等）：它们是圆角或构形过渡特征，其半径通常可通过相关关键点及主尺寸推导，GB/T 14689推荐仅主特征标注，圆角可选注。
- “middle”点、某些辅助线段：仅辅助形状、无必要单独注释。
- 多余短线（如内槽多分段）已用关键尺寸标注表达，不必重复式。


Then call the tool to complete the annotation task.
you can use tools: {"linear dimension" : to deal with linear length, 
                    "linear offset dimension" : to deal with distance dimension.}
'''


def safe_extract_json_array_block(text: str) -> str:
    """
    从任意 GPT 返回内容中提取第一个合法的 JSON 数组段落
    """
    text = text.strip()

    # 以 `[` 开头、以 `]` 结尾的 JSON 数组块
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]

    raise ValueError("未找到 JSON 块")

class GPTAutoDimensionAgent:
    def __init__(self, tools, system_prompt=None):
        self.system_prompt = system_prompt or example_prompt
        self.tools = tools

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

    def generate_dimension_plan(self, result: json) -> str:
        load_dotenv()

        from tools.deepseek_wrapper import read_with_done_check
        geometry_data = read_with_done_check(result["geom_data"], result["done_path"])

        with open(result["img_path"], "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode("utf-8")
        image_content = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{img_base64}"
            }
        }

        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"以下是图元数据：\n{json.dumps(geometry_data, ensure_ascii=False, indent=2)}\n,请调用工具完成线性长度标注与距离标注"},
                    image_content
                ]
            }
        ]

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        responses = ''
        functions = self._build_tool_specs()
        
        while True:
            try:
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages,
                    functions=functions,
                    function_call="auto",
                )
            except Exception as e:
                return f"Error detection: {str(e)}"

            message = response.choices[0].message
            messages.append(message)
            print(message.content)
            # content = response.choices[0].message.content
            # if responses:
            #     responses += content + "\n\n"

            if message.function_call:
                func_name = message.function_call.name
                args = json.loads(message.function_call.arguments)
                
                print(f'dimension tool: {func_name}')
                print(f'arg: {args}')

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
                except Exception as e:
                    result = f"Error running tool '{func_name}': {e}"

                print(f'dimension tool run result: {str(result)}')
                messages.append({
                    "role": "function",
                    "name": func_name,
                    "content": str(result)
                })
            else:
                break
        # content = response.choices[0].message.content
        # print(content)
        #
        # try:
        #     json_str = safe_extract_json_array_block(content)
        #     parsed = json.loads(json_str)
        #     with open("C:\\Users\\gyj15\\Desktop\\zw3d\\export\\dimension_recommendation.json", "w", encoding="utf-8") as f:
        #         json.dump(parsed, f, ensure_ascii=False, indent=2)
        #     print("✅ 成功写入 dimension_recommendation.json")
        # except Exception as e:
        #     print(f"[Warn] 写入 JSON 文件失败: {e}")

        return responses
