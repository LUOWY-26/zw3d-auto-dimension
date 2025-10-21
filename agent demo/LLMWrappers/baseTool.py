# -*- coding: utf-8 -*-
"""
tool_base.py  (PROD)
基础工具抽象与自动注册（GPT-5 Tools API 兼容）。
"""
from __future__ import annotations
from typing import Any, Dict, List
import inspect
import os
import json
from datetime import datetime

class Tool:
    """所有工具基类（保持项目约定的 name/description/parameters 接口）。"""
    name: str = "base_tool"
    description: str = "Base tool"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": []
    }

    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    def run(self, **kwargs) -> Any:
        raise NotImplementedError

    @staticmethod
    def ok(data: Any) -> Dict[str, Any]:
        return {"ok": True, "data": data}

    @staticmethod
    def err(msg: str, **extra) -> Dict[str, Any]:
        d = {"ok": False, "error": msg}
        d.update(extra)
        return d

def discover_tools(module) -> List["Tool"]:
    tools: List[Tool] = []
    for name in dir(module):
        obj = getattr(module, name)
        try:
            if inspect.isclass(obj) and issubclass(obj, Tool) and obj is not Tool:
                tools.append(obj())
        except Exception:
            pass
    return tools

def register_all_tools(wrapper, module) -> None:
    """对模块内所有 Tool 子类进行注册。"""
    for t in discover_tools(module):
        wrapper.register_tool(t)


def save_full_messages(messages: list, save_dir: str = "../logs", prefix: str = "dimension_flow"):
    """
    保存整个标注流程的全部 messages 到本地文件（JSON 和 Markdown 两种格式）

    Args:
        messages (list): LLM 流程产生的全部消息列表，例如 run_dialog 返回的 messages
        save_dir (str): 保存目录，默认 ./logs
        prefix (str): 文件名前缀
    """
    os.makedirs(save_dir, exist_ok=True)  # 自动创建目录

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = os.path.join(save_dir, f"{prefix}_{now}")

    # 保存 JSON（完整数据，可复现）
    with open(f"{base_path}.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    # 保存 Markdown（可读性更好）
    with open(f"{base_path}.md", "w", encoding="utf-8") as f:
        for msg in messages:
            role = msg.get("role", "unknown")
            if role == "user":
                role_icon = "👤 用户"
            elif role == "assistant":
                role_icon = "🤖 助手"
            elif role == "tool":
                role_icon = "🔧 工具"
            else:
                role_icon = f"❓ {role}"

            f.write(f"**{role_icon}**:\n\n{msg.get('content', '')}\n\n---\n\n")

    print(f"✅ 已保存完整标注流程到 {base_path}.json / {base_path}.md")
