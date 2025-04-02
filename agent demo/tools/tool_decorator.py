import re
from functools import wraps

def auto_fallback_if_incomplete(fallback_method_name="execute_multi_step"):
    def decorator(method):
        @wraps(method)
        def wrapper(self, user_input, *args, **kwargs):
            result = method(self, user_input, *args, **kwargs)

            if "TOOL_CALL" in result and "No valid tool call" not in result:
                tool_count = getattr(self, "_tool_count", None)
                #判断可能有多个指定（然后。。。）但是只生成了一个TOOL_CALL的情况
                if tool_count == 1 and re.search(r"然后|接着|下一步|多个工具|还需要|第二步|接下来", result, re.I):
                    print("[Fallback] 触发多步骤执行 fallback")
                    fallback_method = getattr(self, fallback_method_name)
                    last_tool_call = getattr(self, "_last_tool_call", None)

                    return fallback_method(user_input, skip_first=last_tool_call)
            return result
        return wrapper
    return decorator


