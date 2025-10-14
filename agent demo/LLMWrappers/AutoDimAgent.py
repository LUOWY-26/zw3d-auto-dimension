# -*- coding: utf-8 -*-
"""
Auto dimension agent
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import json, os, re, base64
from LLMWrappers.GPT5Wrapper import GPTToolWrapper
from LLMWrappers.baseTool import save_full_messages

AUTO_DIM_SYS_PROMPT = '''
You are an expert in mechanical drawing dimensioning, well-versed in applying the Chinese national standard GB/T 14689 (Mechanical Drawing - Dimensioning Rules).

Given an engineering drawing image and a set of geometric entities extracted from a 2D projection view (including lines, arcs, and circles), your task is to generate a complete and standardized dimensioning plan.

Strictly follow these stages:

Stage 1: Understand the engineering drawing
- Parse the provided geometry data and image.
- Map each entity ID with its type (line, arc, circle, etc.) and key coordinates.
- Ensure that all referenced IDs exist in the data (do not fabricate IDs).

Stage 2: Determine datum lines
- Select one horizontal and one vertical datum line before creating locating dimensions.
- Choose datum lines according to functional priority, external contour priority, symmetry, or processing/inspection convenience.
- Clearly state the chosen datum lines to ensure consistency.

Stage 3: Mark overall/primary dimensions
- Dimension the external contour and major shape sizes first (e.g., overall width, height, main radii).
- These dimensions establish the main body of the part.

Stage 4: Add locating dimensions
- For all internal features (holes, slots, cutouts, inner rectangles), add locating dimensions relative to the chosen datum lines.
- Include center-to-edge, center-to-center, and edge-to-edge distances to fully define feature positions.
- Ensure consistency by always referencing the same datum lines, avoiding chained dimensioning.

Stage 5: Add feature-specific dimensions
- Apply hole callout dimensions for holes (includes diameter, depth, thread if applicable).
- Use radial dimensions for arcs, especially when arc length is a functional feature.
- Use linear or arc length dimensions as appropriate for non-circular features.

Stage 6: Optimize dimensions
- Apply symmetry or coordinate dimensions where features are symmetric or aligned (if features are symmetric, only annotate one of them).
- If there are any symmetric features, tell me about them.
- Avoid redundant or unnecessary annotations; auxiliary entities should not be directly dimensioned unless required.

Stage 7: Adjust annotation placement
- Place dimension texts and extension lines so they do not overlap or occlude geometry.
- Ensure clarity and readability of all annotations.

Output requirements:
1. Provide a JSON list mapping each labeled entity ID to its dimension type and description.
2. Provide a separate list of entity IDs not directly dimensioned, along with the reason (e.g., auxiliary, redundant).
3. Then, call the appropriate tool functions to complete the annotation task.

Example output:
labeled entities and their label types and descriptions:
[
  {"id":666, "type":"radial", "desc":"Radius of the central circular hole"},
  {"id":656, "type":"radial", "desc":"Radius of the large arc edge"},
  {"id":578, "type":"holecallout", "desc":"Main mounting hole"},
  {"id":1373, "type":"holecallout", "desc":"Datum hole"},
  {"id":268, "type":"linear", "desc":"Bottom edge length of outer contour (width)"},
  {"id":71,  "type":"linear", "desc":"Right vertical edge length of outer contour (height)"},
  {"id":100, "type":"linearoffset", "desc":"Right auxiliary edge (height)"},
  {"id":422, "type":"linearoffset", "desc":"Distance between centers of upper and lower holes"},
  {"id":422, "type":"linearoffset", "desc":"Distance from center of upper hole to right datum edge"}
]

Entities not involved in direct labeling and reasons:
1. Auxiliary lines and points (e.g., X, Y, Centerline): Used only for geometric reference, not annotated independently.
2. Redundant short segments (e.g., segment lines in inner grooves): Covered by primary dimensions, redundant annotations are unnecessary.

Available tools:
{
"linear dimension": for linear length dimension, 
"linear offset dimension": for distance dimension (offset from feature to the datum line), 
"radial dimension": for measuring arc radius, 
"hole callout dimension": for comprehensive hole information dimension 
}
'''

class GPTAutoDimAgent:
    def __init__(self, model: str = None, api_key: Optional[str] = None):
        self.wrapper = GPTToolWrapper(model=model or os.environ.get("MODEL_NAME", "gpt-5"),
                                      api_key=api_key)

    def attach_from_wrapper(self, other: GPTToolWrapper):
        self.wrapper._tools_defs = other._registered_defs
        self.wrapper._registry   = other._registered_exec

    def run(self, system_prompt: str, user_prompt: str,
            history: Optional[List[Dict[str, Any]]] = None,
            tool_choice: Any = "auto", parallel_tool_calls: bool = True) -> Dict[str, Any]:
        msgs = [{"role":"system","content":system_prompt}]
        if history: msgs.extend(history)
        msgs.append({"role":"user","content":user_prompt})
        return self.wrapper.run_dialog(msgs, tool_choice=tool_choice, parallel_tool_calls=parallel_tool_calls)

class GPTAutoDimensionAgent:
    """工程图自动标注 Agent。"""
    def __init__(self, wrapper: GPTToolWrapper, model: str = None):
        self.wrapper = wrapper
        self.model = model or os.environ.get("MODEL_NAME", "gpt-5")

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        """从任意文本中提取第一个 JSON 对象。"""
        if not text:
            return {}
        try:
            return json.loads(text)
        except Exception:
            pass
        m = re.search(r'\{[\s\S]*\}', text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return {}
        return {}

    def generate_dimension_plan(self, std_view_result: Dict[str, Any]) -> Dict[str, Any]:
        from tools.deepseek_wrapper import read_with_done_check
        geometry_data = read_with_done_check(std_view_result.get("geom_data"), std_view_result.get("done_path"))

        with open(std_view_result.get("img_path"), "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode("utf-8")

        messages = [{"role": "system", "content": AUTO_DIM_SYS_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                                "The following is the metadata of the engineering drawing:\n"
                                + json.dumps(geometry_data, ensure_ascii=False, indent=2)
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}",
                            # 可选：分辨率/推理深度，openai 支持 detail: "low"|"high"
                            "detail": "high"
                        }
                    }
                ]
            }
        ]

        result = self.wrapper.run_dialog(messages, tool_choice="auto", parallel_tool_calls=False)
        save_full_messages(result["messages"], prefix="dimension_flow")
        raw_text = result.get("response","") or ""
        parsed = self._extract_json(raw_text)

        return {
            "response": raw_text,
            "json": parsed,
            "messages": result.get("messages", [])
        }
