import tkinter as tk
from tkinter import ttk
import threading
import time
import os
from PIL import Image, ImageTk
import html
import json
from datetime import datetime
import tiktoken
from tools.deepseek_wrapper import DeepseekToolWrapper
# from tools.gpt_wrapper import GPTToolWrapper
from LLMWrappers.GPT5Wrapper import GPTToolWrapper
from tools import zw3d_command_tool
from tools.tool_base import Tool
import importlib
import inspect
import tkinter.messagebox as messagebox
# from tools.zw3d_command_tool import ZW3DCommandTool, ZW3DCommandOpen, ZW3DCommandExpPDF, ZW3DCommandExpDWG, ZW3DCommandExp
# from tools.zw3d_command_tool import ZW3DCommandStdVuCreate, ZW3DCommandSave
from LLMWrappers.baseTool import register_all_tools
import tools.zw3d_command_tool as tools_module

class GUIAPP:
    def __init__(self, root, wrapper):
        self.wrapper = wrapper
        register_all_tools(wrapper, tools_module)
        self.last_user_command = ""

        root.title("CHAT V1.0")
        root.geometry('1000x700')
        root.configure(bg='#FFFFFF')

        self.tab_control = ttk.Notebook(root)
        self.tabs = []
        self.tab_control.pack(fill='both', expand=True)

        self.tab_buttons = tk.Frame(root, bg='#FFFFFF')
        self.tab_buttons.pack(fill='x', padx=10, pady=(5, 0))
        self.new_tab_button = tk.Button(self.tab_buttons, text="🆕 新建会话", command=self.create_new_tab, font=('Microsoft YaHei', 10), bg="#F0F0F0")
        self.new_tab_button.pack(side='left', padx=(0, 5))
        self.close_tab_button = tk.Button(self.tab_buttons, text="❌ 删除当前会话", command=self.delete_current_tab, font=('Microsoft YaHei', 10), bg="#F0F0F0")
        self.close_tab_button.pack(side='left')

        self.create_new_tab()

        self.input_frame = tk.Frame(root, bg='#FFFFFF')
        self.input_frame.pack(fill='x', padx=10, pady=(0, 10), side='bottom')

        self.input_text = tk.Text(self.input_frame, font=('Microsoft YaHei', 12), height=3, wrap='word', bg='#FFFFFF', fg='#000000')
        self.input_text.pack(side='left', fill='both', expand=True, padx=(0, 5))
        self.input_text.bind('<Return>', self.execute_command)
        self.input_text.bind('<Shift-Return>', self.insert_newline)
        self.input_text.bind('<Up>', self.insert_last_command)
        self.input_text.bind('<KeyRelease>', self.update_token_count)

        self.token_label = tk.Label(root, text="Tokens: 0", font=('Microsoft YaHei', 9), fg="#666666", bg="#FFFFFF")
        self.token_label.pack(anchor='e', padx=10, pady=(0, 5))

        self.resend_button = tk.Button(self.input_frame, text="🔁重发", command=self.resend_last_command,
                                       font=('Microsoft YaHei', 12), bg='#FFFFFF', fg='#000000')
        self.resend_button.pack(side='right', padx=(5, 0))

        self.save_button = tk.Button(self.input_frame, text="💾保存", command=self.save_chat_history,
                                     font=('Microsoft YaHei', 12), bg='#FFFFFF', fg='#000000')
        self.save_button.pack(side='right', padx=(5, 0))

        self.send_button = tk.Button(self.input_frame, text="📤发送", command=self.execute_command,
                                     font=('Microsoft YaHei', 12), bg='#FFFFFF', fg='#000000')
        self.send_button.pack(side='right', padx=(5, 0))

        self.tab_control.bind("<<NotebookTabChanged>>", self.restore_last_user_command)

        self.stop_thinking = threading.Event()

    def update_token_count(self, event=None):
        content = self.input_text.get("1.0", 'end').strip()
        enc = tiktoken.get_encoding("cl100k_base")
        token_count = len(enc.encode(content))
        self.token_label.config(text=f"Tokens: {token_count}")

    def build_prompt_from_history(self, current_input, max_tokens=1000000):
        enc = tiktoken.get_encoding("cl100k_base")
        session = self.get_current_session()

        # 拿到历史消息
        all_messages = session["history"].copy()
        # # 加上当前用户输入
        # all_messages.append({"role": "user", "content": current_input})

        # 限制 token 数量
        accumulated = []
        total_tokens = 0
        for msg in reversed(all_messages):
            tokens = enc.encode(msg["content"])
            if total_tokens + len(tokens) > max_tokens:
                break
            accumulated.insert(0, msg)
            total_tokens += len(tokens)

        return accumulated

    def create_new_tab(self):
        frame = tk.Frame(self.tab_control, bg='#FFFFFF')
        canvas = tk.Canvas(frame, bg='#FFFFFF', bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        chat_frame = tk.Frame(canvas, bg='#FFFFFF')

        chat_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        chat_window = canvas.create_window((0, 0), window=chat_frame, anchor='nw')
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(chat_window, width=e.width))

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side='right', fill='y')

        session = {
            "frame": frame,
            "canvas": canvas,
            "chat_frame": chat_frame,
            "scrollbar": scrollbar,
            "history": [],
            "last_user_command": ""
        }

        self.tabs.append(session)
        self.tab_control.add(frame, text=f"会话 {len(self.tabs)}")
        self.tab_control.select(len(self.tabs) - 1)

    def delete_current_tab(self):
        index = self.tab_control.index("current")
        if len(self.tabs) > 1:
            self.tab_control.forget(index)
            del self.tabs[index]

    def get_current_session(self):
        return self.tabs[self.tab_control.index("current")]

    def add_message(self, text, sender="user", return_label=False):
        session = self.get_current_session()
        outer_frame = tk.Frame(session["chat_frame"], bg='#FFFFFF')
        is_user = sender == "user"
        align = 'e' if is_user else 'w'
        avatar_path = "avatar_user.png" if is_user else "avatar_ai.png"

        message_frame = tk.Frame(outer_frame, bg='#FFFFFF')
        message_frame.pack(side='right' if is_user else 'left', anchor=align)

        if os.path.exists(avatar_path):
            img = Image.open(avatar_path).resize((32, 32))
            avatar_img = ImageTk.PhotoImage(img)
            avatar_label = tk.Label(message_frame, image=avatar_img, bg='#FFFFFF')
            avatar_label.image = avatar_img
            avatar_label.pack(side='right' if is_user else 'left', padx=5)

        bubble = tk.Label(
            message_frame,
            text=text,
            bg="#D1E7DD" if is_user else "#F1F0F0",
            fg="#000000",
            justify='left',
            anchor='w',
            font=('Microsoft YaHei', 12),
            wraplength=700,
            padx=10,
            pady=5
        )
        bubble.pack(side='right' if is_user else 'left', padx=5, pady=2)

        timestamp = time.strftime("%H:%M:%S")
        ts_label = tk.Label(outer_frame, text=timestamp, font=('Microsoft YaHei', 8), fg="#888888", bg="#FFFFFF")
        ts_label.pack(anchor=align, padx=5)

        outer_frame.pack(anchor=align, pady=5, padx=10, fill='x')
        session["canvas"].update_idletasks()

        # 延迟滚动
        session["canvas"].after(100, lambda: session["canvas"].yview_moveto(1.0))

        session["history"].append({"role": sender, "content": text})

        if return_label:
            return bubble

    def execute_command(self, event=None):
        if isinstance(event, tk.Event) and event.state == 1:
            return

        command = self.input_text.get("1.0", 'end').strip()
        if command.lower() in ['exit', 'quit']:
            exit()
        if command:
            session = self.get_current_session()
            session["last_user_command"] = command
            self.input_text.delete("1.0", 'end')
            self.add_message(command, sender="user")
            self.input_text.config(state='disabled')
            self.send_button.config(state='disabled')
            threading.Thread(target=self.run_llm, args=(command,)).start()
        return "break"

    def insert_newline(self, event=None):
        self.input_text.insert(tk.INSERT, "\n")
        return "break"

    def animate_thinking(self, label_widget):
        dots = ""
        while not self.stop_thinking.is_set():
            dots += "."
            if len(dots) > 3:
                dots = ""
            try:
                label_widget.config(text=f"正在思考{dots}")
            except:
                break  # 防止界面被关闭后异常
            time.sleep(0.5)  # 每0.5秒更新一次

    def run_llm(self, command):
        thinking_label = self.add_message("正在思考...", sender="assistant", return_label=True)
        prompt = self.build_prompt_from_history(command)

        self.stop_thinking.clear()
        threading.Thread(target=self.animate_thinking, args=(thinking_label,)).start()

        try:
            response = self.wrapper.run_dialog(prompt)
            formatted = self.preprocess_response(response)
            self.stop_thinking.set()
            self.animate_typing(thinking_label, formatted)
            self.get_current_session()["history"][-1]["content"] = formatted
        except Exception as e:
            self.stop_thinking.set()
            import tkinter.messagebox as messagebox
            messagebox.showerror("错误", f"请求失败：\n{str(e)}")
            thinking_label.config(text="❌ 请求失败")
        finally:
            self.input_text.config(state='normal')
            self.send_button.config(state='normal')

    def animate_typing(self, label, full_text):
        label.config(text="")
        def type_char(i=0):
            if i < len(full_text):
                label.config(text=full_text[:i+1])
                label.after(15, type_char, i+1)
        type_char()

    def insert_last_command(self, event=None):
        last = self.get_current_session()["last_user_command"]
        if last:
            self.input_text.delete("1.0", 'end')
            self.input_text.insert("1.0", last)

    def resend_last_command(self):
        last = self.get_current_session()["last_user_command"]
        if last:
            self.input_text.delete("1.0", 'end')
            self.input_text.insert("1.0", last)
            self.execute_command()

    def preprocess_response(self, text):
        # import re
        # text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        # text = re.sub(r"`([^`]*)`", r"[代码: \1]", text)
        return text["response"]

    def save_chat_history(self):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        tab_index = self.tab_control.index(self.tab_control.select()) + 1
        filename = f"chat_history_{now}_会话{tab_index}.json"
        history = self.get_current_session()["history"]
        try:
            with open(f"{filename}.json", "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            with open(f"{filename}.md", "w", encoding="utf-8") as f:
                for msg in history:
                    role = "🤖" if msg["role"] == "agent" else "👤"
                    f.write(f"**{role}**:\n\n{msg['content']}\n\n---\n\n")
            messagebox.showinfo("保存成功", f"聊天记录已保存为：\n{filename}")
        except Exception as e:
            messagebox.showerror("保存失败", f"出现错误：\n{str(e)}")

    def restore_last_user_command(self, event=None):
        last = self.get_current_session()["last_user_command"]
        self.input_text.delete("1.0", 'end')
        self.input_text.insert("1.0", last)



# def register_all_tools(wrapper):
#     for name, obj in inspect.getmembers(zw3d_command_tool):
#         if inspect.isclass(obj) and issubclass(obj, Tool) and obj is not Tool:
#             try:
#                 wrapper.register_tool(obj())
#                 print(f"✅ 注册工具: {obj.__name__}")
#             except Exception as e:
#                 print(f"❌ 注册失败: {obj.__name__}, 原因: {e}")


if __name__ == "__main__":
    # wrapper = DeepseekToolWrapper()
    wrapper = GPTToolWrapper()

    root = tk.Tk()
    app = GUIAPP(root, wrapper)
    root.mainloop()