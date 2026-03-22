import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk

# ---------- 全局配置 ----------
PROGRESS_NAMES = [
    "Nether", "Bastion", "Fortress", "Blind",
    "Stronghold", "End", "Finish"
]
BACKGROUND_FILES = [
    "1nether.png", "2bastion.png", "3fortress.png",
    "4blind.png", "5stronghold.png", "6end.png", "7finish.png"
]
PROGRESS_TO_BG = {
    "Nether": "1nether.png",
    "Bastion": "2bastion.png",
    "Fortress": "3fortress.png",
    "Blind": "4blind.png",
    "Stronghold": "5stronghold.png",
    "End": "6end.png",
    "Finish": "7finish.png"
}

START_TYPES = {
    "宝藏(Buried_treasure)": "Buried_treasure",
    "废门(Ruined_portal)": "Ruined_portal",
    "村庄(Village)": "Village",
    "神殿(Temple)": "Temple",
    "沉船(Shipwreck)": "Shipwreck"
}
BASTION_TYPES = {
    "藏宝室(Treasure)": "Treasure",
    "居住区(Housing)": "Housing",
    "棚(Stable)": "Stable",
    "桥(Bridge)": "Bridge"
}
START_TYPES_LIST = list(START_TYPES.keys())
BASTION_TYPES_LIST = list(BASTION_TYPES.keys())

SPEEDRUN_TYPES = ["RSG", "SSG", "FSG", "ZSG", "Ranked", "Casual", "Private"]

CONFIG_FILE = "config.json"

# 默认文字坐标（用于重置本地图片）
DEFAULT_TEXT_X = 100
DEFAULT_TEXT_Y = 100

# ---------- 主应用 ----------
class SpeedrunCoverMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("我的世界速通封面一键制作工具")
        self.root.geometry("1280x800")
        self.root.minsize(800, 600)

        # 标志位，防止重置坐标时触发配置保存
        self.resetting_coords = False

        # 数据变量
        self.seed_var = tk.StringVar()
        self.match_id_var = tk.StringVar()
        self.start_type_var = tk.StringVar(value="")
        self.bastion_type_var = tk.StringVar(value="")
        self.speedrun_type_var = tk.StringVar(value="")

        # 高级模式种子
        self.advanced_mode = tk.BooleanVar(value=False)
        self.seed_overworld = tk.StringVar()
        self.seed_nether = tk.StringVar()
        self.seed_end = tk.StringVar()
        self.seed_rng = tk.StringVar()

        # 背景
        self.bg_mode = tk.IntVar(value=1)            # 1=自动，2=手动
        self.manual_bg_type = tk.IntVar(value=1)     # 1=内置，2=本地
        self.manual_bg_var = tk.StringVar(value="1nether.png")
        self.local_bg_path = tk.StringVar()

        # 进度数据
        self.progress_min = []
        self.progress_sec = []
        self.progress_completed = []
        for _ in PROGRESS_NAMES:
            self.progress_min.append(tk.StringVar())
            self.progress_sec.append(tk.StringVar())
            self.progress_completed.append(tk.BooleanVar(value=True))

        # 文字样式（会保存到配置）
        self.align_var = tk.StringVar(value="left")
        self.font_size_var = tk.IntVar(value=100)
        self.text_color_var = tk.StringVar(value="#FFFFFF")
        self.text_x_var = tk.IntVar(value=DEFAULT_TEXT_X)
        self.text_y_var = tk.IntVar(value=DEFAULT_TEXT_Y)
        self.font_path_var = tk.StringVar(value="")
        self.line_spacing_var = tk.IntVar(value=80)
        self.bold_var = tk.BooleanVar(value=False)
        self.italic_var = tk.BooleanVar(value=False)

        # 文件名自定义
        self.filename_include_seed = tk.BooleanVar(value=True)
        self.filename_include_matchid = tk.BooleanVar(value=False)
        self.filename_include_start = tk.BooleanVar(value=False)
        self.filename_include_bastion = tk.BooleanVar(value=False)
        self.filename_include_speedrun_type = tk.BooleanVar(value=False)
        self.filename_include_final_time = tk.BooleanVar(value=True)
        self.filename_include_final_progress = tk.BooleanVar(value=True)

        # 预览图像
        self.preview_img = None
        self.preview_canvas = None

        # 加载配置
        self.load_config()

        # 构建UI
        self.create_widgets()

        # 绑定配置保存
        self.bind_config_save()

        # 初始化预览
        self.update_preview()

    def create_widgets(self):
        # 主框架
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # 左侧控制区
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        left_canvas = tk.Canvas(left_frame, highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=left_canvas.yview)
        left_scrollable = ttk.Frame(left_canvas)
        left_scrollable.bind("<Configure>", lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
        left_canvas.create_window((0,0), window=left_scrollable, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 右侧预览区
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        self.preview_canvas = tk.Canvas(right_frame, bg='gray', highlightthickness=0)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        self.preview_canvas.bind('<Configure>', self.on_preview_resize)

        # ---------- 左侧内容 ----------
        row = 0

        # 种子信息
        seed_frame = ttk.LabelFrame(left_scrollable, text="种子信息")
        seed_frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        row += 1

        ttk.Label(seed_frame, text="种子码:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        seed_entry = ttk.Entry(seed_frame, textvariable=self.seed_var, width=20)
        seed_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        ttk.Button(seed_frame, text="粘贴", command=lambda: self.seed_var.set(self.root.clipboard_get())).grid(row=0, column=2, padx=5)

        advanced_cb = ttk.Checkbutton(seed_frame, text="高级模式（多维度种子）", variable=self.advanced_mode,
                                      command=self.toggle_advanced_seed)
        advanced_cb.grid(row=1, column=0, columnspan=3, padx=5, pady=2, sticky="w")

        self.advanced_frame = ttk.Frame(seed_frame)
        self.advanced_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
        self.advanced_frame.grid_remove()

        ttk.Label(self.advanced_frame, text="Overworld:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(self.advanced_frame, textvariable=self.seed_overworld, width=15).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(self.advanced_frame, text="Nether:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(self.advanced_frame, textvariable=self.seed_nether, width=15).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(self.advanced_frame, text="The End:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(self.advanced_frame, textvariable=self.seed_end, width=15).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(self.advanced_frame, text="RNG:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(self.advanced_frame, textvariable=self.seed_rng, width=15).grid(row=3, column=1, padx=5, pady=2)
        ttk.Button(self.advanced_frame, text="粘贴多行种子", command=self.paste_advanced_seeds).grid(row=4, column=0, columnspan=2, pady=5)

        # 速通类型
        ttk.Label(seed_frame, text="速通类型:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        speedrun_combo = ttk.Combobox(seed_frame, textvariable=self.speedrun_type_var, values=SPEEDRUN_TYPES, width=20)
        speedrun_combo.grid(row=3, column=1, padx=5, pady=2, sticky="w")

        # 比赛ID
        ttk.Label(seed_frame, text="比赛ID:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        match_entry = ttk.Entry(seed_frame, textvariable=self.match_id_var, width=20)
        match_entry.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        # 开局类型
        ttk.Label(seed_frame, text="开局类型:").grid(row=5, column=0, padx=5, pady=2, sticky="w")
        start_combo = ttk.Combobox(seed_frame, textvariable=self.start_type_var, values=START_TYPES_LIST, width=20)
        start_combo.grid(row=5, column=1, padx=5, pady=2, sticky="w")

        # 猪堡类型
        ttk.Label(seed_frame, text="猪堡类型:").grid(row=6, column=0, padx=5, pady=2, sticky="w")
        bastion_combo = ttk.Combobox(seed_frame, textvariable=self.bastion_type_var, values=BASTION_TYPES_LIST, width=20)
        bastion_combo.grid(row=6, column=1, padx=5, pady=2, sticky="w")

        seed_frame.columnconfigure(1, weight=1)

        # Pace 输入
        pace_frame = ttk.LabelFrame(left_scrollable, text="进度时间 (分:秒)")
        pace_frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        row += 1

        ttk.Label(pace_frame, text="进度", width=12).grid(row=0, column=0, padx=2, pady=2)
        ttk.Label(pace_frame, text="分", width=5).grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(pace_frame, text="秒", width=5).grid(row=0, column=2, padx=2, pady=2)
        ttk.Label(pace_frame, text="完成", width=5).grid(row=0, column=3, padx=2, pady=2)

        for i, name in enumerate(PROGRESS_NAMES):
            ttk.Label(pace_frame, text=name, width=12).grid(row=i+1, column=0, padx=2, pady=2)
            spin_min = ttk.Spinbox(pace_frame, from_=0, to=99, width=5, textvariable=self.progress_min[i])
            spin_min.grid(row=i+1, column=1, padx=2, pady=2)
            spin_sec = ttk.Spinbox(pace_frame, from_=0, to=59, width=5, textvariable=self.progress_sec[i])
            spin_sec.grid(row=i+1, column=2, padx=2, pady=2)
            chk = ttk.Checkbutton(pace_frame, variable=self.progress_completed[i])
            chk.grid(row=i+1, column=3, padx=2, pady=2)

        # 背景选择
        bg_frame = ttk.LabelFrame(left_scrollable, text="背景图片")
        bg_frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        row += 1

        ttk.Radiobutton(bg_frame, text="自动根据最终进度", variable=self.bg_mode, value=1).pack(anchor="w", padx=5, pady=2)
        manual_rb = ttk.Radiobutton(bg_frame, text="手动选择", variable=self.bg_mode, value=2)
        manual_rb.pack(anchor="w", padx=5, pady=2)

        self.manual_subframe = ttk.Frame(bg_frame)
        self.manual_subframe.pack(fill=tk.X, padx=5, pady=2)

        ttk.Radiobutton(self.manual_subframe, text="内置背景", variable=self.manual_bg_type, value=1).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(self.manual_subframe, text="本地选择", variable=self.manual_bg_type, value=2).pack(side=tk.LEFT, padx=5)

        self.builtin_frame = ttk.Frame(self.manual_subframe)
        self.local_frame = ttk.Frame(self.manual_subframe)

        ttk.Label(self.builtin_frame, text="选择:").pack(side=tk.LEFT)
        bg_combo = ttk.Combobox(self.builtin_frame, textvariable=self.manual_bg_var, values=BACKGROUND_FILES, width=15)
        bg_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(self.local_frame, text="选择本地图片", command=self.select_local_bg).pack(side=tk.LEFT, padx=5)
        ttk.Label(self.local_frame, textvariable=self.local_bg_path, wraplength=150).pack(side=tk.LEFT, padx=5)

        self.update_manual_bg_ui()

        def on_manual_bg_type_change(*args):
            self.update_manual_bg_ui()
        self.manual_bg_type.trace_add("write", on_manual_bg_type_change)

        def on_bg_mode_change(*args):
            if self.bg_mode.get() == 1:
                self.manual_subframe.pack_forget()
            else:
                self.manual_subframe.pack(fill=tk.X, padx=5, pady=2)
                self.update_manual_bg_ui()
        self.bg_mode.trace_add("write", on_bg_mode_change)
        on_bg_mode_change()

        # 文字样式
        text_style_frame = ttk.LabelFrame(left_scrollable, text="文字样式")
        text_style_frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        row += 1

        ttk.Label(text_style_frame, text="对齐:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        align_combo = ttk.Combobox(text_style_frame, textvariable=self.align_var, values=["left", "center", "right"], width=8)
        align_combo.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(text_style_frame, text="字号:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        ttk.Spinbox(text_style_frame, from_=10, to=200, width=5, textvariable=self.font_size_var).grid(row=0, column=3, padx=5, pady=2)
        ttk.Label(text_style_frame, text="行距:").grid(row=0, column=4, padx=5, pady=2, sticky="w")
        ttk.Spinbox(text_style_frame, from_=20, to=200, width=5, textvariable=self.line_spacing_var).grid(row=0, column=5, padx=5, pady=2)

        ttk.Label(text_style_frame, text="X偏移:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Spinbox(text_style_frame, from_=0, to=2560, width=6, textvariable=self.text_x_var).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(text_style_frame, text="Y偏移:").grid(row=1, column=2, padx=5, pady=2, sticky="w")
        ttk.Spinbox(text_style_frame, from_=0, to=1476, width=6, textvariable=self.text_y_var).grid(row=1, column=3, padx=5, pady=2)
        ttk.Button(text_style_frame, text="颜色", command=self.choose_color).grid(row=1, column=4, padx=5, pady=2)

        font_frame = ttk.Frame(text_style_frame)
        font_frame.grid(row=2, column=0, columnspan=6, padx=5, pady=2, sticky="ew")
        ttk.Label(font_frame, text="字体:").pack(side=tk.LEFT)
        ttk.Button(font_frame, text="选择字体文件", command=self.select_font_file).pack(side=tk.LEFT, padx=5)
        ttk.Label(font_frame, textvariable=self.font_path_var, wraplength=200).pack(side=tk.LEFT, fill=tk.X, expand=True)

        style_frame = ttk.Frame(text_style_frame)
        style_frame.grid(row=3, column=0, columnspan=6, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(style_frame, text="加粗", variable=self.bold_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(style_frame, text="斜体", variable=self.italic_var).pack(side=tk.LEFT, padx=5)

        # 输出文件名自定义
        naming_frame = ttk.LabelFrame(left_scrollable, text="输出文件名自定义")
        naming_frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        row += 1

        ttk.Checkbutton(naming_frame, text="种子码", variable=self.filename_include_seed).pack(anchor="w", padx=5)
        ttk.Checkbutton(naming_frame, text="比赛ID", variable=self.filename_include_matchid).pack(anchor="w", padx=5)
        ttk.Checkbutton(naming_frame, text="开局类型", variable=self.filename_include_start).pack(anchor="w", padx=5)
        ttk.Checkbutton(naming_frame, text="猪堡类型", variable=self.filename_include_bastion).pack(anchor="w", padx=5)
        ttk.Checkbutton(naming_frame, text="速通类型", variable=self.filename_include_speedrun_type).pack(anchor="w", padx=5)
        ttk.Checkbutton(naming_frame, text="最终时间", variable=self.filename_include_final_time).pack(anchor="w", padx=5)
        ttk.Checkbutton(naming_frame, text="最终进度", variable=self.filename_include_final_progress).pack(anchor="w", padx=5)

        # 按钮
        btn_frame = ttk.Frame(left_scrollable)
        btn_frame.grid(row=row, column=0, padx=5, pady=10, sticky="ew")
        row += 1
        ttk.Button(btn_frame, text="生成并保存", command=self.save_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="刷新预览", command=self.update_preview).pack(side=tk.LEFT, padx=5)

        left_scrollable.columnconfigure(0, weight=1)

        # 绑定更新事件
        for var in [self.align_var, self.font_size_var, self.text_color_var, self.text_x_var, self.text_y_var,
                    self.font_path_var, self.line_spacing_var, self.bold_var, self.italic_var]:
            var.trace_add("write", lambda *a: self.update_preview())
        for i in range(len(PROGRESS_NAMES)):
            self.progress_min[i].trace_add("write", lambda *a: self.update_preview())
            self.progress_sec[i].trace_add("write", lambda *a: self.update_preview())
            self.progress_completed[i].trace_add("write", lambda *a: self.update_preview())
        self.bg_mode.trace_add("write", lambda *a: self.update_preview())
        self.manual_bg_var.trace_add("write", lambda *a: self.update_preview())
        self.local_bg_path.trace_add("write", lambda *a: self.update_preview())
        self.seed_var.trace_add("write", lambda *a: self.update_preview())
        self.match_id_var.trace_add("write", lambda *a: self.update_preview())
        self.start_type_var.trace_add("write", lambda *a: self.update_preview())
        self.bastion_type_var.trace_add("write", lambda *a: self.update_preview())
        self.speedrun_type_var.trace_add("write", lambda *a: self.update_preview())
        self.advanced_mode.trace_add("write", lambda *a: self.update_preview())
        for sv in [self.seed_overworld, self.seed_nether, self.seed_end, self.seed_rng]:
            sv.trace_add("write", lambda *a: self.update_preview())

    # ---------- 辅助UI ----------
    def toggle_advanced_seed(self):
        if self.advanced_mode.get():
            self.advanced_frame.grid()
        else:
            self.advanced_frame.grid_remove()

    def paste_advanced_seeds(self):
        try:
            text = self.root.clipboard_get().strip()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if len(lines) > 0:
                self.seed_overworld.set(lines[0])
            if len(lines) > 1:
                self.seed_nether.set(lines[1])
            if len(lines) > 2:
                self.seed_end.set(lines[2])
            if len(lines) > 3:
                self.seed_rng.set(lines[3])
        except:
            pass

    def update_manual_bg_ui(self):
        self.builtin_frame.pack_forget()
        self.local_frame.pack_forget()
        if self.manual_bg_type.get() == 1:
            self.builtin_frame.pack(fill=tk.X, pady=2)
        else:
            self.local_frame.pack(fill=tk.X, pady=2)

    def select_local_bg(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if path:
            self.local_bg_path.set(path)
            # 重置文字坐标到默认值，但不保存到配置
            self.resetting_coords = True
            self.text_x_var.set(DEFAULT_TEXT_X)
            self.text_y_var.set(DEFAULT_TEXT_Y)
            self.resetting_coords = False
            # 刷新预览
            self.update_preview()

    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.text_color_var.get())
        if color[1]:
            self.text_color_var.set(color[1])

    def select_font_file(self):
        path = filedialog.askopenfilename(filetypes=[("TrueType Font", "*.ttf")])
        if path:
            self.font_path_var.set(path)

    # ---------- 配置保存与加载 ----------
    def bind_config_save(self):
        style_vars = [self.align_var, self.font_size_var, self.text_color_var,
                      self.text_x_var, self.text_y_var, self.font_path_var,
                      self.line_spacing_var, self.bold_var, self.italic_var]
        for var in style_vars:
            var.trace_add("write", lambda *a: self.save_config())

    def safe_config_value(self, var, default):
        try:
            val = var.get()
            if val == "" or val is None:
                return default
            if isinstance(default, int):
                return int(val)
            elif isinstance(default, bool):
                return bool(val)
            else:
                return val
        except:
            return default

    def save_config(self):
        # 如果是重置坐标，则跳过保存
        if self.resetting_coords:
            return
        config = {
            "align": self.align_var.get(),
            "font_size": self.safe_config_value(self.font_size_var, 100),
            "text_color": self.text_color_var.get(),
            "text_x": self.safe_config_value(self.text_x_var, DEFAULT_TEXT_X),
            "text_y": self.safe_config_value(self.text_y_var, DEFAULT_TEXT_Y),
            "font_path": self.font_path_var.get(),
            "line_spacing": self.safe_config_value(self.line_spacing_var, 80),
            "bold": self.safe_config_value(self.bold_var, False),
            "italic": self.safe_config_value(self.italic_var, False)
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except:
            pass

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            if "align" in config:
                self.align_var.set(config["align"])
            if "font_size" in config:
                self.font_size_var.set(config["font_size"])
            if "text_color" in config:
                self.text_color_var.set(config["text_color"])
            if "text_x" in config:
                self.text_x_var.set(config["text_x"])
            if "text_y" in config:
                self.text_y_var.set(config["text_y"])
            if "font_path" in config:
                self.font_path_var.set(config["font_path"])
            if "line_spacing" in config:
                self.line_spacing_var.set(config["line_spacing"])
            if "bold" in config:
                self.bold_var.set(config["bold"])
            if "italic" in config:
                self.italic_var.set(config["italic"])
        except:
            pass

    # ---------- 核心功能 ----------
    def safe_int(self, var, default=0):
        try:
            val = var.get()
            if val == "" or val is None:
                return default
            return int(val)
        except:
            return default

    def get_final_progress(self):
        times = []
        for i, name in enumerate(PROGRESS_NAMES):
            if self.progress_completed[i].get():
                mins = self.safe_int(self.progress_min[i])
                secs = self.safe_int(self.progress_sec[i])
                if mins == 0 and secs == 0:
                    continue
                total_seconds = mins * 60 + secs
                times.append((total_seconds, name, i))
        if not times:
            return None
        times.sort(key=lambda x: x[0])
        return times[-1][1]

    def get_final_time(self):
        final_progress = self.get_final_progress()
        if final_progress:
            idx = PROGRESS_NAMES.index(final_progress)
            mins = self.safe_int(self.progress_min[idx])
            secs = self.safe_int(self.progress_sec[idx])
            if mins != 0 or secs != 0:
                return f"{mins}m{secs}s"
        return ""

    def get_seed_string(self, for_filename=False):
        if self.advanced_mode.get():
            seeds = []
            if self.seed_overworld.get().strip():
                seeds.append(("Overworld", self.seed_overworld.get().strip()))
            if self.seed_nether.get().strip():
                seeds.append(("Nether", self.seed_nether.get().strip()))
            if self.seed_end.get().strip():
                seeds.append(("The End", self.seed_end.get().strip()))
            if self.seed_rng.get().strip():
                seeds.append(("RNG", self.seed_rng.get().strip()))
            if not seeds:
                return "" if for_filename else None
            if for_filename:
                return "_".join([val for _, val in seeds])
            else:
                return "\n".join([f"{dim}: {val}" for dim, val in seeds])
        else:
            seed = self.seed_var.get().strip()
            if for_filename:
                return seed
            else:
                return f"seed: {seed}" if seed else ""

    def get_match_id_string(self, for_filename=False):
        mid = self.match_id_var.get().strip()
        if not mid:
            return ""
        if for_filename:
            return f"matchid{mid}"
        else:
            return f"Match ID: {mid}"

    def get_start_type_string(self, for_filename=False):
        start = self.start_type_var.get()
        if start and start in START_TYPES:
            return START_TYPES[start] if for_filename else start.split('(')[0]
        return ""

    def get_bastion_type_string(self, for_filename=False):
        bastion = self.bastion_type_var.get()
        if bastion and bastion in BASTION_TYPES:
            return BASTION_TYPES[bastion] if for_filename else bastion.split('(')[0]
        return ""

    def get_text_lines(self):
        lines = []
        seed_text = self.get_seed_string(for_filename=False)
        if seed_text:
            if "\n" in seed_text:
                lines.extend(seed_text.split("\n"))
            else:
                lines.append(seed_text)
        match_text = self.get_match_id_string(for_filename=False)
        if match_text:
            lines.append(match_text)
        speedrun = self.speedrun_type_var.get().strip()
        if speedrun:
            lines.append(f"Category: {speedrun}")
        start = self.get_start_type_string(for_filename=False)
        if start:
            lines.append(f"Start: {start}")
        bastion = self.get_bastion_type_string(for_filename=False)
        if bastion:
            lines.append(f"Bastion: {bastion}")
        times = []
        for i, name in enumerate(PROGRESS_NAMES):
            if self.progress_completed[i].get():
                mins = self.safe_int(self.progress_min[i])
                secs = self.safe_int(self.progress_sec[i])
                if mins == 0 and secs == 0:
                    continue
                total_sec = mins * 60 + secs
                times.append((total_sec, name, i))
        times.sort(key=lambda x: x[0])
        for _, name, i in times:
            mins = self.safe_int(self.progress_min[i])
            secs = self.safe_int(self.progress_sec[i])
            lines.append(f"{name}: {mins}:{secs:02d}")
        return lines

    def get_background_image(self):
        if self.bg_mode.get() == 1:
            final = self.get_final_progress()
            if final is None:
                bg_file = BACKGROUND_FILES[0]
            else:
                bg_file = PROGRESS_TO_BG.get(final, BACKGROUND_FILES[0])
            path = os.path.join(os.path.dirname(__file__), bg_file)
        else:
            if self.manual_bg_type.get() == 1:
                path = os.path.join(os.path.dirname(__file__), self.manual_bg_var.get())
            else:
                if self.local_bg_path.get():
                    path = self.local_bg_path.get()
                else:
                    path = os.path.join(os.path.dirname(__file__), "1nether.png")
        try:
            img = Image.open(path).convert("RGBA")
            return img
        except Exception as e:
            messagebox.showerror("错误", f"无法加载背景图片：{path}\n{e}")
            return Image.new("RGBA", (800, 600), (0,0,0,255))

    def load_font(self, size):
        font_path = self.font_path_var.get().strip()
        bold = self.bold_var.get()
        italic = self.italic_var.get()
        if font_path and os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                pass
        common_fonts = [
            "simhei.ttf", "msyh.ttc", "Microsoft YaHei.ttf", "arial.ttf"
        ]
        for font_name in common_fonts:
            try:
                font = ImageFont.truetype(font_name, size)
                if bold or italic:
                    try:
                        variant = 0
                        if bold:
                            variant |= ImageFont.BOLD
                        if italic:
                            variant |= ImageFont.ITALIC
                        font = font.font_variant(variant=variant)
                    except:
                        pass
                return font
            except:
                continue
        return ImageFont.load_default()

    def render_image(self):
        bg = self.get_background_image().copy()
        draw = ImageDraw.Draw(bg)
        lines = self.get_text_lines()
        if not lines:
            return bg

        font = self.load_font(self.safe_int(self.font_size_var, 100))
        color = self.text_color_var.get()
        x0 = self.safe_int(self.text_x_var, DEFAULT_TEXT_X)
        y0 = self.safe_int(self.text_y_var, DEFAULT_TEXT_Y)
        line_spacing = self.safe_int(self.line_spacing_var, 80)

        y = y0
        for line in lines:
            bbox = draw.textbbox((0,0), line, font=font)
            text_width = bbox[2] - bbox[0]
            align = self.align_var.get()
            if align == "left":
                x = x0
            elif align == "center":
                x = x0 - text_width // 2
            else:
                x = x0 - text_width
            draw.text((x, y), line, font=font, fill=color)
            y += line_spacing
        return bg

    def on_preview_resize(self, event):
        self.update_preview()

    def update_preview(self):
        try:
            img = self.render_image()
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            if canvas_width <= 1 or canvas_height <= 1:
                return
            img_width, img_height = img.size
            scale = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            img_preview = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.preview_img = ImageTk.PhotoImage(img_preview)
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(canvas_width//2, canvas_height//2, image=self.preview_img, anchor="center")
        except Exception as e:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(10, 10, text=f"预览错误: {e}", anchor="nw", fill="red")

    def generate_filename(self):
        parts = []
        if self.filename_include_seed.get():
            seed = self.get_seed_string(for_filename=True)
            if seed:
                parts.append(seed)
        if self.filename_include_matchid.get():
            match_id = self.get_match_id_string(for_filename=True)
            if match_id:
                parts.append(match_id)
        if self.filename_include_start.get():
            start = self.get_start_type_string(for_filename=True)
            if start:
                parts.append(start)
        if self.filename_include_bastion.get():
            bastion = self.get_bastion_type_string(for_filename=True)
            if bastion:
                parts.append(bastion)
        if self.filename_include_speedrun_type.get():
            speedrun = self.speedrun_type_var.get().strip()
            if speedrun:
                parts.append(speedrun)
        if self.filename_include_final_time.get():
            final_time = self.get_final_time()
            if final_time:
                parts.append(final_time)
        if self.filename_include_final_progress.get():
            final_progress = self.get_final_progress()
            if final_progress:
                parts.append(final_progress)

        if not parts:
            parts.append("cover")
        name = "_".join(parts) + ".png"
        invalid_chars = r'[<>:"/\\|?*]'
        for ch in invalid_chars:
            name = name.replace(ch, '_')
        return name

    def save_image(self):
        try:
            img = self.render_image()
            filename = self.generate_filename()
            save_path = filedialog.asksaveasfilename(defaultextension=".png", initialfile=filename,
                                                      filetypes=[("PNG files", "*.png")])
            if save_path:
                img.save(save_path, "PNG")
                messagebox.showinfo("成功", f"图片已保存至：{save_path}")
        except Exception as e:
            messagebox.showerror("保存错误", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedrunCoverMaker(root)
    root.mainloop()