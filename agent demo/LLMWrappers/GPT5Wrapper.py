# -*- coding: utf-8 -*-
"""
- 自动注册工具
- 处理 tool_calls 并以 role="tool"+tool_call_id 回传
- 在调用 "zw3d_stdvucrt_dim" 且 return code == 1 时自动触发 GPTAutoDimensionAgent
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Callable
from openai import OpenAI
import json, os, traceback
import tiktoken
import time, json

LOG_PATH = os.getenv("AUTO_DIM_TOOL_LOG", "tool_calls.jsonl")

def count_messages_tokens(messages, model="gpt-4-1"):
    """
    统计 messages 列表的 token 数量
    :param messages: OpenAI API 的 messages 列表，例如：
        [
            {"role": "system", "content": "你是助手"},
            {"role": "user", "content": "请帮我画一个圆"}
        ]
    :param model: 模型名称，决定编码方式
    :return: (总token数, 每条消息对应的token数列表)
    """
    # 选择合适的 tokenizer
    enc = tiktoken.encoding_for_model(model)

    token_counts = []
    total = 0
    for msg in messages:
        # content 可能是 str 或 list
        if isinstance(msg["content"], str):
            text = msg["content"]
        elif isinstance(msg["content"], list):
            # multimodal: 拼接里面的 text 部分
            text = " ".join(
                [c["text"] for c in msg["content"] if c["type"] == "text"]
            )
        else:
            text = str(msg["content"])

        tokens = len(enc.encode(msg.get("role", "") + " " + text))
        token_counts.append(tokens)
        total += tokens

    return total, token_counts

class GPTToolWrapper:
    def __init__(self, model: str = None, api_key: Optional[str] = None):
        self.model = model or os.environ.get("MODEL_NAME", "gpt-5")
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        self._tools_defs: List[Dict[str, Any]] = []
        self._registry: Dict[str, Callable[..., Any]] = {}

    def _log_jsonl(self, obj: dict):
        """安全写日志"""
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")
        except Exception:
            pass

    # 注册
    def register_tool(self, tool_obj) -> None:
        self._tools_defs.append(tool_obj.get_tool_definition())
        def _exec(**kwargs):
            return tool_obj.run(**kwargs)
        self._registry[tool_obj.name] = _exec

    # 暴露（给 Agent 共享）
    @property
    def _registered_defs(self):
        return self._tools_defs
    @property
    def _registered_exec(self):
        return self._registry

    # 主循环
    def run_dialog(self, messages: List[Dict[str, Any]], tool_choice: Any = "auto",
                   parallel_tool_calls: bool = False, max_rounds: int = 100) -> Dict[str, Any]:
        rounds = 0
        last_raw = None
        while rounds < max_rounds:
            rounds += 1
            kwargs = dict(model=self.model, messages=messages)
            if self._tools_defs:
                kwargs["tools"] = self._tools_defs
                # 只有在存在 tools 时，才允许传 tool_choice / parallel_tool_calls
                if tool_choice is not None:
                    kwargs["tool_choice"] = tool_choice
                kwargs["parallel_tool_calls"] = parallel_tool_calls
            else:
                pass

            resp = self.client.chat.completions.create(**kwargs)

            last_raw = resp
            reply = resp.choices[0].message
            messages.append({
                "role": "assistant",
                "content": reply.content or "",
                "tool_calls": [tc.model_dump() for tc in (reply.tool_calls or [])]
            })

            if not reply.tool_calls:
                print (count_messages_tokens(messages))
                return {"messages": messages, "response": reply.content or "", "raw": last_raw}

            for tc in reply.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments or "{}")
                exec_fn = self._registry.get(name)

                # === 日志：开始 ===
                self._log_jsonl({
                    "event": "tool_start",
                    "tool_call_id": tc.id,
                    "name": name,
                    "args": args,
                    "ts": time.time()
                })

                # 执行工具
                try:
                    result = exec_fn(**args) if exec_fn else {"ok": False, "error": f"Unknown tool: {name}"}
                    error = None
                except Exception as e:
                    result = {"ok": False, "error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()}
                    print ("exception:", name, tc.id, count_messages_tokens(messages))
                    error = str(e)

                # === 日志：结束 ===
                self._log_jsonl({
                    "event": "tool_end",
                    "tool_call_id": tc.id,
                    "name": name,
                    "result": result if error is None else None,
                    "error": error,
                    "ts": time.time()
                })

                # 条件触发自动标注 Agent
                try:
                    if (name == "zw3d_stdvucrt_dim"
                        # and isinstance(result, dict)
                        and (result.get("data") or {}).get("return code") == 1):
                        # and result.get("return code") == 1):
                        from LLMWrappers.AutoDimAgent import GPTAutoDimensionAgent
                        # 控制台与 GUI 可见提示
                        print("⚙️ 已进入自动标注 Agent，正在生成标注计划...")
                        # messages.append({"role":"assistant","content":"⚙️ 已进入自动标注 Agent，正在生成标注计划..."})
                        auto_agent = GPTAutoDimensionAgent(wrapper=self, model=self.model)
                        auto_res = auto_agent.generate_dimension_plan(result.get("data", {}))
                        packed = result.get("data", {}).copy()
                        packed["auto_dimension"] = auto_res
                        result = {"ok": True, "data": packed}
                except Exception as _e:
                    result = {"ok": False, "error": f"auto_dim_failed: {_e}"}

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })
        print (messages, count_messages_tokens(messages))
        return {"messages": messages, "response": "(工具调用轮次已达上限)", "raw": last_raw}
