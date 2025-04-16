import openai, base64, json
from dotenv import load_dotenv
import os

example_prompt = '''
你是一位工程图尺寸标注专家，擅长按照《机械制图 尺寸注法》（GB/T 14689）等国家标准进行尺寸标注。
请结合用户提供的工程图图像和供一组从工程视图中提取的几何图元信息（包含直线、圆弧和圆），你需要首先将图像与图元数据（包含实体的id和关键点的坐标）一一关联起来，

然后请你判断：
1. 哪些位置应进行尺寸标注；
2. 应采用何种类型的标注（linear线性、radial半径、diameter直径、angle角度、ordinate坐标、symmetry对称等）；
3. 应如何标注尺寸数值和文字；
4. 应将标注放置于何处，相互之间不会遮挡覆盖；

请确保：
1. 标注满足完备性，能完整表达几何形状和关键尺寸。
2. 对于几何形状的定位标注，例如几何图形内部的几何图形到外部几何图形的距离能通过linear offset标注清晰表达。
3. 不重复、不冗余，例如封闭轮廓不需重复标注
4. 对称/阵列特征可使用对称尺寸或孔标注
5. 检查id是否正确，是否在用户提供的图元数据中，避免编造不存在的id

🧾 请返回如下格式的 JSON 输出：
[
  {{
    "type": "linear length",
    "id": 156,
    "points": [[10, 20], [100, 20]],
    "value": "90",
    "text point": [55, 30],
    "note": "外框底边长度"
  }},
  {{
    "type": "linear distance",
    "id": [134, 144],
    "points": [[10, 20], [100, 20]],
    "value": "100",
    "text point": [55, 10],
    "note": "中间圆的圆心到外侧矩形右边框的距离(point to line distance)"
  }},
  {{
    "type": "linear distance",
    "id": [256, 189],
    "value": "80",
    "text point": [100, 20],
    "note": "左安装孔中心到外侧矩形下边框的距离(point to line distance)"
  }},
  {{
    "type": "radial",
    "id": 98,
    "center": [50, 50],
    "radius": 20,
    "value": "R20",
    "text point": [55, 30],
    "note": "风扇轮廓半径"
  }}
]。
'''

class GPTAutoDimensionAgent:
    def __init__(self, system_prompt=None):
        self.system_prompt = system_prompt or example_prompt

    def generate_dimension_plan(self, result: json) -> dict:

        load_dotenv()

        # 图像 base64 编码
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
                    {"type": "text", "text": f"以下是图元数据：\n{json.dumps(geometry_data, ensure_ascii=False, indent=2)}\n"},
                    image_content
                ]
            }
        ]

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # or use env variable

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            temperature=0.3
        )

        content = response.choices[0].message.content
        print(content)
        try:
            return {"dimension recommendation": content}
        except Exception:
            return {"error": "返回错误", "raw": content}
