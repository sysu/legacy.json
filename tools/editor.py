import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
from dataclasses import dataclass, field
from typing import Any, Callable
from datetime import datetime

FIELD_SPECS = [
    ("id", "id", "单行文本", "提供便于识别的标识符。软件可能使用此字段建立索引。\n- 标识性：与项目具有关联性，可从id联想到项目\n- 层次：必要时可使用多段描述拼接\n- 哈希友好：不易与其他项目id碰撞\n- 长度：一般不建议超过200字符\n注意：id来源于内部称呼、简写、秘密代号等，公众称呼请用names字段。"),
    ("update_time", "update_time", "只读文本", "项目和legacy.json文件最后更新的时间。\n保存时自动生成，使用 RFC 3339 格式。"),  
    ("update_executor", "update_executor", "单行文本", "项目和legacy.json文件最后更新的执行者。\n通常是编辑者的名称，必要时可使用集体名称。"),
    ("commit_sha", "commit_sha", "单行文本", "项目归档状态的git commit sha值。"),
    ("names", "names", "字符串数组", "项目的名称，可能是内部名称、技术管理中的名称。\n此字段是字符串数组，可能被搜索引擎或人工智能程序检索。"),
    ("formal_names", "formal_names", "字符串数组", "项目的公开名称。\n这是历史上公众或相关方对该项目的称呼。"),
    ("planning", "planning", "多行文本", "记录项目计划信息，包括：\n- 项目背景、详细故事和事件\n- 具体人物及其构思\n- 项目产生、发展、技术选择、重要变革、决策\n- 项目功能、受众、管理、模块划分、重要文档等设想\n必要时可引用人物言论、历史文献、法律法规等。"),
    ("description", "description", "多行文本", "记录最终项目状态和技术状态。\n内容应具体、逻辑连贯，只说明已发生的事情，反映已实现的真实状态。\n面向研究、教育、调研、二次利用等场景，提供关键、细致、深刻而确切的信息。"),
    ("formal_description", "formal_description", "多行文本", "记录公众感知的项目状态和技术状态。\n作为历史遗产项目，主要记录并反映当时的公众互动。\n内容不应再次概括，仅保存历史上项目如何描述自身的记录，作为历史证据保存。"),
    ("available_times", "available_times", "时间范围数组", "记录项目曾经可用的时间段。\n每个元素包含开始和结束时间，使用 RFC 3339 格式。\n时间跨度可短至数月，长至数年。"),
    ("documentation", "documentation", "多行文本", "记录项目的文档信息。\n包括用户手册、开发者文档、社区文档等。\n内容可直接包含文档，或提供互联网链接地址，或指向仓库中的地址。"),
    ("milestones", "milestones", "时间多行数组", "记录项目的里程碑信息。\n每个条目有一个标题（时间），内容为描述文字。\n里程碑应具有真实性和时间跨度（如间隔数月或数年）。"),
    ("keywords", "keywords", "字符串数组", "描述项目的关键字。\n可能被搜索引擎或人工智能程序检索。"),
    ("resources", "resources", "多行键值数组", "描述与项目有关的研究性资源，帮助进一步了解项目。\n每个条目有一个标题，内容为详细描述，可包含链接。"),
    ("influencers", "influencers", "多行键值数组", "描述项目的创建者、重要贡献者、需要特别提及的帮助者。\n每个条目有一个标题（称呼），内容说明贡献、历史作用、相关信息和联系方式，可包含链接。"),
    ("extras", "extras", "多行键值数组", "读者可能感兴趣的额外信息。\n每个条目有一个标题，内容为详细信息。"),
    ("disciplines", "disciplines", "字符串数组", "说明项目相关的学科和研究应用领域。\n优先使用公认、含义清晰、教育机构公开使用的名词。"),
    ("subsequents", "subsequents", "多行键值数组", "说明项目的后继项目。\n每个条目有一个标题（项目名称），内容说明后续关系，可包含链接。"),
]

@dataclass
class Field:
    name: str
    value: Any = None
    missing: str = "缺失"

    def get(self) -> Any:
        return self.missing if self.value is None else self.value

    def is_empty(self) -> bool:
        return self.value is None or self.value == ""

@dataclass
class Document:
    id: Field = field(default_factory=lambda: Field("id"))
    update_time: Field = field(default_factory=lambda: Field("update_time"))
    update_executor: Field = field(default_factory=lambda: Field("update_executor"))
    commit_sha: Field = field(default_factory=lambda: Field("commit_sha"))
    names: Field = field(default_factory=lambda: Field("names", []))
    formal_names: Field = field(default_factory=lambda: Field("formal_names", []))
    planning: Field = field(default_factory=lambda: Field("planning"))
    description: Field = field(default_factory=lambda: Field("description"))
    formal_description: Field = field(default_factory=lambda: Field("formal_description"))
    available_times: Field = field(default_factory=lambda: Field("available_times", []))
    documentation: Field = field(default_factory=lambda: Field("documentation", []))
    milestones: Field = field(default_factory=lambda: Field("milestones", []))
    keywords: Field = field(default_factory=lambda: Field("keywords", []))
    resources: Field = field(default_factory=lambda: Field("resources", []))
    influencers: Field = field(default_factory=lambda: Field("influencers", []))
    extras: Field = field(default_factory=lambda: Field("extras", []))
    disciplines: Field = field(default_factory=lambda: Field("disciplines", []))
    subsequents: Field = field(default_factory=lambda: Field("subsequents", []))

    def to_dict(self) -> dict:
        result = {}
        for k in self.__dict__:
            v = getattr(self, k)
            if isinstance(v, Field):
                val = v.value
                if isinstance(val, list):
                    val = val.copy()
                result[k] = val
        return result

    @staticmethod
    def from_dict(data: dict) -> "Document":
        doc = Document()
        for k, v in data.items():
            if hasattr(doc, k):
                f = getattr(doc, k)
                if isinstance(f, Field):
                    f.value = v
        return doc

class FieldLabel(tk.Frame):
    def __init__(self, parent, title, description, field_type):
        super().__init__(parent, bg="#f0f0f0", padx=10, pady=8)
        self.field_type = field_type
        tk.Label(self, text=title, font=("Microsoft YaHei", 10, "bold"),
                 bg="#f0f0f0", fg="#333").pack(anchor="w")
        tk.Label(self, text=description, font=("Microsoft YaHei", 8),
                 bg="#f0f0f0", fg="#666", wraplength=300).pack(anchor="w")

class SingleLineInput(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white", padx=15, pady=10)
        self.var = tk.StringVar()
        entry_frame = tk.Frame(self, bg="#f0f0f0")
        entry_frame.pack(fill="x")
        tk.Entry(entry_frame, textvariable=self.var, font=("Microsoft YaHei", 11),
                 bg="#f0f0f0", bd=0, relief="flat", insertwidth=2).pack(fill="x", padx=12, pady=8)

    def get(self) -> str:
        return self.var.get()

    def set(self, value: str):
        self.var.set(value or "")

class ReadOnlyInput(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white", padx=15, pady=10)
        label_frame = tk.Frame(self, bg="#f0f0f0")
        label_frame.pack(fill="x")
        self.label = tk.Label(label_frame, text="", font=("Microsoft YaHei", 11),
                             bg="#f0f0f0", fg="#666", anchor="w")
        self.label.pack(fill="x", padx=12, pady=8)

    def get(self) -> str:
        return self.label.cget("text")

    def set(self, value: str):
        self.label.config(text=value or "")

class MultiLineInput(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white", padx=15, pady=10)
        text_frame = tk.Frame(self, bg="#f0f0f0")
        text_frame.pack(fill="x")
        self.text = tk.Text(text_frame, font=("Microsoft YaHei", 11),
                            bg="#f0f0f0", bd=0, relief="flat",
                            height=15, wrap="word", insertwidth=2)
        self.text.pack(fill="x", padx=12, pady=8)

    def get(self) -> str:
        return self.text.get("1.0", "end-1c")

    def set(self, value: str):
        self.text.delete("1.0", "end")
        if value:
            self.text.insert("1.0", value)

class StringArrayInput(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white", padx=15, pady=10)
        self.items = []
        self.item_frames = []
        self.entry_var = tk.StringVar()
        entry_frame = tk.Frame(self, bg="#f0f0f0")
        entry_frame.pack(fill="x", pady=(0, 8))
        tk.Entry(entry_frame, textvariable=self.entry_var, font=("Microsoft YaHei", 11),
                 bg="#f0f0f0", bd=0, relief="flat", insertwidth=2).pack(side="left", fill="x", expand=True, padx=12, pady=8)
        add_btn = tk.Button(entry_frame, text="添加", font=("Microsoft YaHei", 10),
                           bg="#4a90d9", fg="white", bd=0, relief="flat", padx=15, pady=5,
                           command=self.add_item)
        add_btn.pack(side="right")

        scroll_frame = tk.Frame(self, bg="white")
        scroll_frame.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(scroll_frame, bg="#cccccc", troughcolor="#f0f0f0", width=16)
        scrollbar.pack(side="right", fill="y")
        canvas = tk.Canvas(scroll_frame, bg="white", bd=0, highlightthickness=0,
                          yscrollcommand=scrollbar.set)
        scrollbar.config(command=canvas.yview)
        canvas.pack(side="left", fill="both", expand=True)

        self.list_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=self.list_frame, anchor="nw", tags="list_window")
        self.list_frame.bind("<Configure>",
                            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<MouseWheel>", on_mousewheel)
        self.list_frame.bind("<MouseWheel>", on_mousewheel)

    def add_item(self):
        item = self.entry_var.get().strip()
        if not item:
            return
        self.entry_var.set("")
        self.items.append(item)
        self._create_item_row(len(self.items) - 1)

    def _create_item_row(self, idx):
        item_frame = tk.Frame(self.list_frame, bg="#f8f8f8", padx=12, pady=8)
        item_frame.pack(fill="x", pady=(0, 5))
        tk.Label(item_frame, text=self.items[idx], font=("Microsoft YaHei", 11),
                 bg="#f8f8f8", fg="#333", anchor="w").pack(side="left", fill="x", expand=True)
        del_btn = tk.Button(item_frame, text="×", font=("Microsoft YaHei", 12, "bold"),
                           bg="#f8f8f8", fg="#999", bd=0, relief="flat", padx=8,
                           command=lambda: self._remove_item(idx))
        del_btn.pack(side="right")

    def _remove_item(self, idx):
        self.items.pop(idx)
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for i in range(len(self.items)):
            self._create_item_row(i)

    def get(self) -> list:
        return self.items.copy()

    def set(self, value: list):
        self.items = value.copy() if value else []
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for i in range(len(self.items)):
            self._create_item_row(i)

class TimelineInput(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white", padx=15, pady=10)
        self.items = []
        self.time_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        input_frame = tk.Frame(self, bg="#f0f0f0")
        input_frame.pack(fill="x", pady=(0, 8))
        time_inner = tk.Frame(input_frame, bg="#f0f0f0")
        time_inner.pack(fill="x", padx=12, pady=8)
        tk.Label(time_inner, text="时间:", font=("Microsoft YaHei", 10), bg="#f0f0f0").pack(side="left")
        tk.Entry(time_inner, textvariable=self.time_var, font=("Microsoft YaHei", 11),
                 bg="#f0f0f0", bd=0, relief="flat", insertwidth=2, width=22).pack(side="left", padx=(8, 15))
        tk.Label(time_inner, text="描述:", font=("Microsoft YaHei", 10), bg="#f0f0f0").pack(side="left")
        tk.Entry(time_inner, textvariable=self.desc_var, font=("Microsoft YaHei", 11),
                 bg="#f0f0f0", bd=0, relief="flat", insertwidth=2).pack(side="left", fill="x", expand=True, padx=8)
        add_btn = tk.Button(time_inner, text="添加", font=("Microsoft YaHei", 10),
                           bg="#4a90d9", fg="white", bd=0, relief="flat", padx=15, pady=5,
                           command=self.add_item)
        add_btn.pack(side="right")
        self.list_frame = tk.Frame(self, bg="white")
        self.list_frame.pack(fill="x")

    def add_item(self):
        time = self.time_var.get().strip()
        if not time:
            return
        desc = self.desc_var.get().strip()
        self.time_var.set("")
        self.desc_var.set("")
        self.items.append([time, desc])
        self._create_item_row(len(self.items) - 1)

    def _create_item_row(self, idx):
        item = self.items[idx]
        item_frame = tk.Frame(self.list_frame, bg="#f8f8f8", padx=12, pady=8)
        item_frame.pack(fill="x", pady=(0, 5))
        time_label = tk.Label(item_frame, text=item[0], font=("Microsoft YaHei", 11, "bold"),
                             bg="#f8f8f8", fg="#333")
        time_label.pack(side="left", anchor="w")
        if len(item) > 1 and item[1]:
            tk.Label(item_frame, text=" - ", font=("Microsoft YaHei", 11),
                     bg="#f8f8f8", fg="#666").pack(side="left")
            tk.Label(item_frame, text=item[1], font=("Microsoft YaHei", 11),
                     bg="#f8f8f8", fg="#666").pack(side="left", anchor="w")
        del_btn = tk.Button(item_frame, text="×", font=("Microsoft YaHei", 12, "bold"),
                           bg="#f8f8f8", fg="#999", bd=0, relief="flat", padx=8,
                           command=lambda: self._remove_item(idx))
        del_btn.pack(side="right")

    def _remove_item(self, idx):
        self.items.pop(idx)
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for i in range(len(self.items)):
            self._create_item_row(i)

    def get(self) -> list:
        return self.items.copy()

    def set(self, value: list):
        self.items = value.copy() if value else []
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for i in range(len(self.items)):
            self._create_item_row(i)

class MultiLineKeyValueInput(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white", padx=15, pady=10)
        self.items = []
        self.key_var = tk.StringVar()
        input_frame = tk.Frame(self, bg="#f0f0f0")
        input_frame.pack(fill="x", pady=(0, 8))
        input_inner = tk.Frame(input_frame, bg="#f0f0f0")
        input_inner.pack(fill="x", padx=12, pady=8)
        tk.Label(input_inner, text="标题：  ", font=("Microsoft YaHei", 10), bg="#f0f0f0").pack(side="left")
        tk.Entry(input_inner, textvariable=self.key_var, font=("Microsoft YaHei", 11),
                 bg="#f0f0f0", bd=0, relief="flat", insertwidth=2, width=18).pack(side="left", padx=(8, 15))
        add_btn = tk.Button(input_inner, text="添加", font=("Microsoft YaHei", 10),
                           bg="#4a90d9", fg="white", bd=0, relief="flat", padx=15, pady=5,
                           command=self.add_item)
        add_btn.pack(side="right")
        content_frame = tk.Frame(input_frame, bg="#f0f0f0")
        content_frame.pack(fill="x", padx=12, pady=(0, 8))
        self.content_text = tk.Text(content_frame, font=("Microsoft YaHei", 11),
                                    bg="#f0f0f0", bd=0, relief="flat", insertwidth=2,
                                    height=3, wrap="word")
        self.content_text.pack(fill="x", padx=12, pady=8)
        self.list_frame = tk.Frame(self, bg="white")
        self.list_frame.pack(fill="x")

    def add_item(self):
        key = self.key_var.get().strip()
        if not key:
            return
        content = self.content_text.get("1.0", "end-1c").strip()
        self.key_var.set("")
        self.content_text.delete("1.0", "end")
        self.items.append(f"{key}\n{content}" if content else key)
        self._create_item_row(len(self.items) - 1)

    def _create_item_row(self, idx):
        item = self.items[idx]
        lines = item.split("\n")
        item_frame = tk.Frame(self.list_frame, bg="#f8f8f8", padx=12, pady=8)
        item_frame.pack(fill="x", pady=(0, 5))
        header_frame = tk.Frame(item_frame, bg="#f8f8f8")
        header_frame.pack(fill="x")
        tk.Label(header_frame, text=lines[0], font=("Microsoft YaHei", 11, "bold"),
                 bg="#f8f8f8", fg="#333", anchor="w").pack(side="left", fill="x", expand=True)
        del_btn = tk.Button(header_frame, text="×", font=("Microsoft YaHei", 12, "bold"),
                           bg="#f8f8f8", fg="#999", bd=0, relief="flat", padx=8)
        del_btn.config(command=lambda btn=del_btn, i=idx: self._remove_item(i))
        del_btn.pack(side="right")
        if len(lines) > 1:
            content_frame = tk.Frame(item_frame, bg="#f8f8f8", pady=8)
            content_frame.pack(fill="x", pady=(8, 0))
            text_content = "\n".join(lines[1:])
            tk.Label(content_frame, text=text_content, font=("Microsoft YaHei", 10),
                    bg="#f8f8f8", fg="#666", anchor="w", justify="left",
                    wraplength=500).pack(fill="x")

    def _remove_item(self, idx):
        self.items.pop(idx)
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for i in range(len(self.items)):
            self._create_item_row(i)

    def get(self) -> list:
        return self.items.copy()

    def set(self, value: list):
        self.items = value.copy() if value else []
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for i in range(len(self.items)):
            self._create_item_row(i)

class TimeMultiLineInput(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white", padx=15, pady=10)
        self.items = []
        self.time_var = tk.StringVar()
        input_frame = tk.Frame(self, bg="#f0f0f0")
        input_frame.pack(fill="x", pady=(0, 8))
        input_inner = tk.Frame(input_frame, bg="#f0f0f0")
        input_inner.pack(fill="x", padx=12, pady=8)
        tk.Label(input_inner, text="时间：  ", font=("Microsoft YaHei", 10), bg="#f0f0f0").pack(side="left")
        tk.Entry(input_inner, textvariable=self.time_var, font=("Microsoft YaHei", 11),
                 bg="#f0f0f0", bd=0, relief="flat", insertwidth=2, width=22).pack(side="left", padx=(8, 15))
        add_btn = tk.Button(input_inner, text="添加", font=("Microsoft YaHei", 10),
                           bg="#4a90d9", fg="white", bd=0, relief="flat", padx=15, pady=5,
                           command=self.add_item)
        add_btn.pack(side="right")
        content_frame = tk.Frame(input_frame, bg="#f0f0f0")
        content_frame.pack(fill="x", padx=12, pady=(0, 8))
        self.content_text = tk.Text(content_frame, font=("Microsoft YaHei", 11),
                                    bg="#f0f0f0", bd=0, relief="flat", insertwidth=2,
                                    height=3, wrap="word")
        self.content_text.pack(fill="x", padx=12, pady=8)
        self.list_frame = tk.Frame(self, bg="white")
        self.list_frame.pack(fill="x")

    def add_item(self):
        time = self.time_var.get().strip()
        if not time:
            return
        content = self.content_text.get("1.0", "end-1c").strip()
        self.time_var.set("")
        self.content_text.delete("1.0", "end")
        self.items.append(f"{time}\n{content}" if content else time)
        self._create_item_row(len(self.items) - 1)

    def _create_item_row(self, idx):
        item = self.items[idx]
        lines = item.split("\n")
        item_frame = tk.Frame(self.list_frame, bg="#f8f8f8", padx=12, pady=8)
        item_frame.pack(fill="x", pady=(0, 5))
        header_frame = tk.Frame(item_frame, bg="#f8f8f8")
        header_frame.pack(fill="x")
        tk.Label(header_frame, text=lines[0], font=("Microsoft YaHei", 11, "bold"),
                 bg="#f8f8f8", fg="#333", anchor="w").pack(side="left", fill="x", expand=True)
        del_btn = tk.Button(header_frame, text="×", font=("Microsoft YaHei", 12, "bold"),
                           bg="#f8f8f8", fg="#999", bd=0, relief="flat", padx=8)
        del_btn.config(command=lambda btn=del_btn, i=idx: self._remove_item(i))
        del_btn.pack(side="right")
        if len(lines) > 1:
            content_frame = tk.Frame(item_frame, bg="#f8f8f8", pady=8)
            content_frame.pack(fill="x", pady=(8, 0))
            text_content = "\n".join(lines[1:])
            tk.Label(content_frame, text=text_content, font=("Microsoft YaHei", 10),
                    bg="#f8f8f8", fg="#666", anchor="w", justify="left",
                    wraplength=500).pack(fill="x")

    def _remove_item(self, idx):
        self.items.pop(idx)
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for i in range(len(self.items)):
            self._create_item_row(i)

    def get(self) -> list:
        result = []
        for item in self.items:
            lines = item.split("\n", 1)
            time = lines[0]
            desc = lines[1] if len(lines) > 1 else ""
            result.append([time, desc])
        return result

    def set(self, value: list):
        raw = value if value else []
        self.items = []
        for entry in raw:
            if isinstance(entry, list) and len(entry) >= 1:
                time = entry[0] or ""
                desc = entry[1] if len(entry) > 1 else ""
                self.items.append(f"{time}\n{desc}" if desc else time)
            elif isinstance(entry, str):
                self.items.append(entry)
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for i in range(len(self.items)):
            self._create_item_row(i)

class TimeRangeInput(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white", padx=15, pady=10)
        self.items = []
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()
        input_frame = tk.Frame(self, bg="#f0f0f0")
        input_frame.pack(fill="x", pady=(0, 8))
        input_inner = tk.Frame(input_frame, bg="#f0f0f0")
        input_inner.pack(fill="x", padx=12, pady=8)
        tk.Label(input_inner, text="开始:", font=("Microsoft YaHei", 10), bg="#f0f0f0").pack(side="left")
        tk.Entry(input_inner, textvariable=self.start_var, font=("Microsoft YaHei", 11),
                 bg="#f0f0f0", bd=0, relief="flat", insertwidth=2, width=22).pack(side="left", padx=(8, 15))
        tk.Label(input_inner, text="结束:", font=("Microsoft YaHei", 10), bg="#f0f0f0").pack(side="left")
        tk.Entry(input_inner, textvariable=self.end_var, font=("Microsoft YaHei", 11),
                 bg="#f0f0f0", bd=0, relief="flat", insertwidth=2, width=22).pack(side="left", padx=(8, 15))
        add_btn = tk.Button(input_inner, text="添加", font=("Microsoft YaHei", 10),
                           bg="#4a90d9", fg="white", bd=0, relief="flat", padx=15, pady=5,
                           command=self.add_item)
        add_btn.pack(side="right")
        self.list_frame = tk.Frame(self, bg="white")
        self.list_frame.pack(fill="x")

    def add_item(self):
        start = self.start_var.get().strip()
        if not start:
            return
        end = self.end_var.get().strip()
        self.start_var.set("")
        self.end_var.set("")
        self.items.append([start, end])
        self._create_item_row(len(self.items) - 1)

    def _create_item_row(self, idx):
        item = self.items[idx]
        item_frame = tk.Frame(self.list_frame, bg="#f8f8f8", padx=12, pady=8)
        item_frame.pack(fill="x", pady=(0, 5))
        header_frame = tk.Frame(item_frame, bg="#f8f8f8")
        header_frame.pack(fill="x")
        end_time = item[1] if len(item) > 1 and item[1] else "至今"
        display_text = f"可用时间：从 {item[0]} 到 {end_time}"
        tk.Label(header_frame, text=display_text, font=("Microsoft YaHei", 11),
                 bg="#f8f8f8", fg="#333", anchor="w").pack(side="left", fill="x", expand=True)
        del_btn = tk.Button(header_frame, text="×", font=("Microsoft YaHei", 12, "bold"),
                           bg="#f8f8f8", fg="#999", bd=0, relief="flat", padx=8)
        del_btn.config(command=lambda btn=del_btn, i=idx: self._remove_item(i))
        del_btn.pack(side="right")

    def _remove_item(self, idx):
        self.items.pop(idx)
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for i in range(len(self.items)):
            self._create_item_row(i)

    def get(self) -> list:
        return self.items.copy()

    def set(self, value: list):
        self.items = value.copy() if value else []
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for i in range(len(self.items)):
            self._create_item_row(i)

COMPONENT_MAP = {
    "单行文本": SingleLineInput,
    "只读文本": ReadOnlyInput,
    "多行文本": MultiLineInput,
    "字符串数组": StringArrayInput,
    "时间范围数组": TimeRangeInput,
    "时间多行数组": TimeMultiLineInput,
    "时间数组": TimelineInput,
    "时间文本数组": TimelineInput,
    "多行键值数组": MultiLineKeyValueInput,
}

class FileService:
    @staticmethod
    def load(path: str) -> Document:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Document.from_dict(data)

    @staticmethod
    def save(doc: Document, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc.to_dict(), f, ensure_ascii=False, indent=2)

class HelpWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("帮助")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        self.build_ui()

    def build_ui(self):
        main_frame = tk.Frame(self, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True)

        title_label = tk.Label(main_frame, text="legacy.json 编辑器",
                               font=("Microsoft YaHei", 14, "bold"),
                               bg="#f0f0f0", fg="#2c3e50", pady=15)
        title_label.pack()

        text_frame = tk.Frame(main_frame, bg="#f0f0f0", padx=15, pady=15)
        text_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        text_widget = tk.Text(text_frame, font=("Microsoft YaHei", 10),
                              bg="#f0f0f0", fg="#333", wrap="word", padx=10, pady=10,
                              bd=0, relief="flat")
        scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview,
                                bg="#cccccc", troughcolor="#f0f0f0",
                                width=16)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        text_widget.pack(side="left", fill="both", expand=True)

        help_text = """
legacy.json 编辑器

简介：
本编辑器用于创建和编辑 legacy.json 文件，记录历史遗产项目的元数据信息。

主要功能：
1. 文件操作：新建、打开、保存、另存为
2. 字段编辑：选择左侧字段列表进行编辑
3. 自动时间：update_time 字段会在保存时自动生成

字段类型说明：
- 单行文本：如 id、commit_sha
- 多行文本：如 planning、description
- 字符串数组：如 names、keywords、disciplines
- 时间范围数组：available_times（开始时间和结束时间）
- 时间多行数组：milestones（时间+描述）
- 多行键值数组：resources、influencers、extras、subsequents

格式要求：
- 日期时间格式：推荐使用 RFC 3339 格式，如 2025-05-11T14:30:00+08:00
- 所有字段均可为空，缺失时显示"缺失"

快捷键：
暂未实现

注意事项：
- 撤销/重做功能尚未完成
- 建议定期保存文件以防数据丢失
"""
        text_widget.insert("1.0", help_text.strip())
        text_widget.config(state="disabled")

        def on_help_mousewheel(event):
            text_widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
        text_widget.bind("<MouseWheel>", on_help_mousewheel)

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("legacy.json 编辑器")
        self.file_path = None
        self.document = Document()
        self.dirty = False
        self.components = {}
        self.field_labels = {}
        self.geometry("1000x700")
        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self):
        toolbar = tk.Frame(self, bg="#2c3e50", padx=10, pady=5)
        toolbar.pack(fill="x")
        style = {"bg": "#2c3e50", "fg": "white", "relief": "flat",
                 "font": ("Microsoft YaHei", 9), "cursor": "hand2",
                 "highlightthickness": 0, "bd": 0,
                 "activebackground": "#2c3e50", "activeforeground": "white",
                 "padx": 6, "pady": 8}
        tk.Button(toolbar, text="新建", command=self.new, **style).pack(side="left", padx=3)
        tk.Button(toolbar, text="打开", command=self.open, **style).pack(side="left", padx=3)
        tk.Button(toolbar, text="保存", command=self.save, **style).pack(side="left", padx=3)
        tk.Button(toolbar, text="另存为", command=self.save_as, **style).pack(side="left", padx=3)
        tk.Frame(toolbar, bg="#2c3e50").pack(side="left", padx=10)
        self.btn_undo = tk.Button(toolbar, text="撤销", command=self.undo, **style)
        self.btn_undo.pack(side="left", padx=3)
        self.btn_redo = tk.Button(toolbar, text="重做", command=self.redo, **style)
        self.btn_redo.pack(side="left", padx=3)

        tk.Label(toolbar, width=10, bg="#2c3e50").pack(side="left")

        self.btn_help = tk.Button(toolbar, text="帮助", command=self.show_help, **style)
        self.btn_help.pack(side="right", padx=3)

        paned = tk.PanedWindow(self, orient="horizontal", sashrelief="raised", sashwidth=6)
        paned.pack(fill="both", expand=True)

        left_panel = tk.Frame(paned, bg="#f0f0f0")
        left_panel.pack_propagate(False)
        paned.add(left_panel, width=300)
        paned.paneconfigure(left_panel, minsize=300)

        scrollbar = tk.Scrollbar(left_panel, orient="vertical")
        canvas = tk.Canvas(left_panel, bg="#f0f0f0", bd=0, highlightthickness=0,
                          yscrollcommand=scrollbar.set)
        scrollbar.config(command=canvas.yview)
        self.field_list = tk.Frame(canvas, bg="#f0f0f0")
        self.field_list.bind("<Configure>",
                            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfigure("field_list_window", width=e.width))
        canvas.create_window((0, 0), window=self.field_list, anchor="nw", tags="field_list_window")
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(0, weight=1)

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<MouseWheel>", on_mousewheel)
        self.field_list.bind("<MouseWheel>", on_mousewheel)
        self._canvas = canvas

        self.field_buttons = {}
        for fname, key, ftype, desc in FIELD_SPECS:
            btn = tk.Label(self.field_list, text=fname, font=("Microsoft YaHei", 10),
                           bg="#ecf0f1", fg="#2c3e50", anchor="w",
                           padx=15, pady=8, cursor="hand2",
                           relief="flat", bd=0,
                           highlightthickness=0, highlightbackground="#ecf0f1")
            btn.pack(fill="x", padx=5, pady=2)
            btn.bind("<Button-1>", lambda e, k=key: self.show_field(k))
            self.field_buttons[key] = btn

        self.editor_panel = tk.Frame(paned, bg="white")
        paned.add(self.editor_panel)

        self.field_title = tk.Label(self.editor_panel, text="选择一个字段",
                                    font=("Microsoft YaHei", 16, "bold"),
                                    bg="white", fg="#2c3e50", anchor="w", padx=20, pady=15)
        self.field_title.pack(fill="x")

        self.field_desc = tk.Label(self.editor_panel, text="",
                                    font=("Microsoft YaHei", 9),
                                    bg="white", fg="#7f8c8d", anchor="w", padx=20,
                                    wraplength=600, justify="left")
        self.field_desc.pack(fill="x")

        self.field_container = tk.Frame(self.editor_panel, bg="white")
        self.field_container.pack(fill="both", expand=True, padx=20, pady=15)

        self.status_bar = tk.Label(self, text="未打开文件", anchor="w",
                                   font=("Microsoft YaHei", 8), bg="#e0e0e0", fg="#444444",
                                   padx=15, pady=5)
        self.status_bar.pack(side="bottom", fill="x")
        separator = tk.Frame(self, height=1, bg="#cccccc")
        separator.pack(side="bottom", fill="x")

        for fname, key, ftype, desc in FIELD_SPECS:
            comp_class = COMPONENT_MAP.get(ftype, SingleLineInput)
            self.components[key] = comp_class(self.field_container)

    def show_field(self, key):
        for child in self.field_container.winfo_children():
            child.pack_forget()
        if key in self.components:
            self.components[key].pack(fill="both", expand=True)
        for fname, k, ftype, desc in FIELD_SPECS:
            if k == key:
                self.field_title.config(text=fname)
                self.field_desc.config(text=desc)
                break
        for k, btn in self.field_buttons.items():
            if k == key:
                btn.config(bg="#d5d8dc")
            else:
                btn.config(bg="#ecf0f1")

    def sync_to_document(self):
        for name, comp in self.components.items():
            if hasattr(self.document, name):
                f = getattr(self.document, name)
                if isinstance(f, Field):
                    f.value = comp.get()

    def sync_from_document(self):
        for name, comp in self.components.items():
            if hasattr(self.document, name):
                f = getattr(self.document, name)
                if isinstance(f, Field):
                    comp.set(f.value)

    def new(self):
        if self.dirty:
            if not messagebox.askyesno("确认", "有未保存的修改，确定要新建吗？"):
                return
        self.document = Document()
        self.file_path = None
        self.dirty = False
        self.sync_from_document()
        self.field_title.config(text="选择一个字段")
        self.field_desc.config(text="")
        for child in self.field_container.winfo_children():
            child.pack_forget()
        self.update_status()

    def open(self):
        if self.dirty:
            if not messagebox.askyesno("确认", "有未保存的修改，确定要打开吗？"):
                return
        path = filedialog.askopenfilename(
            title="打开 legacy.json",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        if path:
            try:
                self.document = FileService.load(path)
                self.file_path = path
                self.dirty = False
                self.sync_from_document()
                self.update_status()
            except Exception as e:
                messagebox.showerror("错误", f"打开文件失败: {e}")

    def save(self):
        if self.file_path:
            self.sync_to_document()
            self.document.update_time.value = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
            try:
                FileService.save(self.document, self.file_path)
                self.dirty = False
                self.sync_from_document()
                self.update_status()
            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败: {e}")
        else:
            self.save_as()

    def save_as(self):
        self.sync_to_document()
        self.document.update_time.value = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        path = filedialog.asksaveasfilename(
            title="另存为",
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        if path:
            try:
                FileService.save(self.document, path)
                self.file_path = path
                self.dirty = False
                self.update_status()
            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败: {e}")

    def show_help(self):
        HelpWindow(self)

    def undo(self):
        messagebox.showinfo("提示", "非常抱歉，没有经费啦，撤销/重做功能未完成。")

    def redo(self):
        messagebox.showinfo("提示", "非常抱歉，没有经费啦，撤销/重做功能未完成。")

    def update_buttons(self):
        pass

    def update_status(self):
        if self.file_path:
            self.status_bar.config(text=f"{self.file_path} {'(已修改)' if self.dirty else ''}")
            filename = self.file_path.split("/")[-1] if "/" in self.file_path else self.file_path.split("\\")[-1]
            self.title(f"legacy.json 编辑器 - {filename}")
        else:
            self.status_bar.config(text="未打开文件")
            self.title("legacy.json 编辑器")

    def on_close(self):
        if self.dirty:
            if not messagebox.askyesno("确认", "有未保存的修改，确定要退出吗？"):
                return
        self.destroy()

if __name__ == "__main__":
    MainWindow().mainloop()