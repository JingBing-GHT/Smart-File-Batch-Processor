"""
图形用户界面模块
Graphical User Interface Module
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
from pathlib import Path
from file_processor import FileProcessor

class FileProcessorGUI:
    """文件处理器图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.processor = FileProcessor()
        self.current_files = []
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(
            main_frame, 
            text="智能文件批量处理工具", 
            font=("Arial", 16, "bold"),
            foreground="#2c3e50"
        )
        title_label.pack(pady=(0, 15))
        
        # 创建标签页控件
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个功能标签页
        self.create_rename_tab()
        self.create_text_replace_tab()
        self.create_format_convert_tab()
        self.create_organize_tab()
        
        # 创建日志显示区域
        self.create_log_area(main_frame)
        
    def create_rename_tab(self):
        """创建重命名标签页"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="📁 批量重命名")
        
        # 文件选择区域
        select_frame = ttk.LabelFrame(tab, text="文件选择", padding="10")
        select_frame.pack(fill=tk.X, pady=5)
        
        # 文件夹选择
        folder_frame = ttk.Frame(select_frame)
        folder_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(folder_frame, text="工作目录:").pack(side=tk.LEFT)
        self.folder_path = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="浏览", command=self.browse_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="刷新", command=self.refresh_files).pack(side=tk.LEFT)
        
        # 文件类型过滤
        filter_frame = ttk.Frame(select_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="文件过滤:").pack(side=tk.LEFT)
        self.file_filter = ttk.Combobox(filter_frame, values=[
            "所有文件", "图片文件", "文档文件", "文本文件", "视频文件", "音频文件"
        ], width=15)
        self.file_filter.set("所有文件")
        self.file_filter.pack(side=tk.LEFT, padx=5)
        self.file_filter.bind('<<ComboboxSelected>>', self.filter_files)
        
        # 文件列表
        list_frame = ttk.LabelFrame(tab, text="文件列表", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建树形视图显示文件列表
        columns = ("文件名", "大小", "修改时间")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # 设置列标题
        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=150)
        
        self.file_tree.column("文件名", width=300)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 重命名规则区域
        rule_frame = ttk.LabelFrame(tab, text="重命名规则", padding="10")
        rule_frame.pack(fill=tk.X, pady=5)
        
        # 命名模式选择
        mode_frame = ttk.Frame(rule_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(mode_frame, text="重命名模式:").pack(side=tk.LEFT)
        self.rename_mode = tk.StringVar(value="pattern")
        
        modes = [
            ("模式命名", "pattern"),
            ("查找替换", "replace"), 
            ("添加前后缀", "prefix")
        ]
        
        for text, mode in modes:
            ttk.Radiobutton(mode_frame, text=text, variable=self.rename_mode, 
                           value=mode).pack(side=tk.LEFT, padx=10)
        
        # 模式命名设置
        self.pattern_frame = ttk.Frame(rule_frame)
        self.pattern_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.pattern_frame, text="命名模板:").pack(side=tk.LEFT)
        self.name_pattern = ttk.Entry(self.pattern_frame, width=30)
        self.name_pattern.insert(0, "文件_{序号}")
        self.name_pattern.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.pattern_frame, text="起始序号:").pack(side=tk.LEFT)
        self.start_number = ttk.Spinbox(self.pattern_frame, from_=1, to=10000, width=8)
        self.start_number.set(1)
        self.start_number.pack(side=tk.LEFT, padx=5)
        
        # 查找替换设置
        self.replace_frame = ttk.Frame(rule_frame)
        self.replace_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.replace_frame, text="查找文本:").pack(side=tk.LEFT)
        self.find_text = ttk.Entry(self.replace_frame, width=20)
        self.find_text.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(self.replace_frame, text="替换为:").pack(side=tk.LEFT)
        self.replace_with = ttk.Entry(self.replace_frame, width=20)
        self.replace_with.pack(side=tk.LEFT, padx=2)
        
        # 前后缀设置
        self.prefix_frame = ttk.Frame(rule_frame)
        self.prefix_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.prefix_frame, text="前缀:").pack(side=tk.LEFT)
        self.prefix_text = ttk.Entry(self.prefix_frame, width=15)
        self.prefix_text.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(self.prefix_frame, text="后缀:").pack(side=tk.LEFT)
        self.suffix_text = ttk.Entry(self.prefix_frame, width=15)
        self.suffix_text.pack(side=tk.LEFT, padx=2)
        
        # 按钮区域
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="预览重命名", command=self.preview_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="执行重命名", command=self.execute_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="撤销操作", command=self.undo_rename).pack(side=tk.LEFT, padx=5)
        
        # 初始显示模式命名框架
        self.show_rename_mode()
        self.rename_mode.trace('w', self.on_rename_mode_change)
    
    def on_rename_mode_change(self, *args):
        """重命名模式改变时的回调"""
        self.show_rename_mode()
    
    def show_rename_mode(self):
        """显示当前重命名模式对应的设置框架"""
        # 隐藏所有框架
        self.pattern_frame.pack_forget()
        self.replace_frame.pack_forget() 
        self.prefix_frame.pack_forget()
        
        # 显示当前模式的框架
        mode = self.rename_mode.get()
        if mode == "pattern":
            self.pattern_frame.pack(fill=tk.X, pady=5)
        elif mode == "replace":
            self.replace_frame.pack(fill=tk.X, pady=5)
        elif mode == "prefix":
            self.prefix_frame.pack(fill=tk.X, pady=5)
    
    def create_text_replace_tab(self):
        """创建文本替换标签页"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="🔍 文本替换")
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(tab, text="文件选择", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_frame, text="选择文本文件:").grid(row=0, column=0, sticky=tk.W)
        self.text_files_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.text_files_var, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="选择文件", command=self.browse_text_files).grid(row=0, column=2)
        
        # 文件列表
        self.text_listbox = tk.Listbox(file_frame, selectmode=tk.EXTENDED, height=6)
        self.text_listbox.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E, pady=5)
        file_frame.columnconfigure(1, weight=1)
        
        # 替换规则区域
        rule_frame = ttk.LabelFrame(tab, text="替换规则", padding="10")
        rule_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(rule_frame, text="查找内容:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.text_find = ttk.Entry(rule_frame, width=50)
        self.text_find.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(rule_frame, text="替换为:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.text_replace = ttk.Entry(rule_frame, width=50)
        self.text_replace.grid(row=1, column=1, padx=5, pady=5)
        
        # 选项设置
        options_frame = ttk.Frame(rule_frame)
        options_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        self.case_sensitive = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="区分大小写", variable=self.case_sensitive).pack(side=tk.LEFT, padx=10)
        
        self.use_regex = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="使用正则表达式", variable=self.use_regex).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(options_frame, text="文件编码:").pack(side=tk.LEFT, padx=10)
        self.file_encoding = ttk.Combobox(options_frame, values=["utf-8", "gbk", "gb2312", "ascii"], width=10)
        self.file_encoding.set("utf-8")
        self.file_encoding.pack(side=tk.LEFT, padx=5)
        
        # 按钮区域
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="预览替换结果", command=self.preview_replace).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="执行替换", command=self.execute_replace).pack(side=tk.LEFT, padx=5)
    
    def create_format_convert_tab(self):
        """创建格式转换标签页"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="🔄 格式转换")
        
        # 图片转换区域
        img_frame = ttk.LabelFrame(tab, text="图片格式转换", padding="10")
        img_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(img_frame, text="选择图片文件:").grid(row=0, column=0, sticky=tk.W)
        self.image_files_var = tk.StringVar()
        ttk.Entry(img_frame, textvariable=self.image_files_var, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(img_frame, text="选择图片", command=self.browse_image_files).grid(row=0, column=2)
        
        # 图片列表
        self.image_listbox = tk.Listbox(img_frame, selectmode=tk.EXTENDED, height=4)
        self.image_listbox.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E, pady=5)
        img_frame.columnconfigure(1, weight=1)
        
        # 转换设置
        convert_frame = ttk.Frame(img_frame)
        convert_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=10)
        
        ttk.Label(convert_frame, text="目标格式:").pack(side=tk.LEFT)
        self.target_format = ttk.Combobox(convert_frame, values=["JPG", "PNG", "WEBP", "BMP", "TIFF"], width=10)
        self.target_format.set("JPG")
        self.target_format.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(convert_frame, text="质量(1-100):").pack(side=tk.LEFT)
        self.quality = ttk.Spinbox(convert_frame, from_=1, to=100, width=8)
        self.quality.set(85)
        self.quality.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(convert_frame, text="转换图片", command=self.convert_images).pack(side=tk.LEFT, padx=20)
        
        # 文档转换区域
        doc_frame = ttk.LabelFrame(tab, text="文档格式转换", padding="10")
        doc_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(doc_frame, text="选择文档文件:").grid(row=0, column=0, sticky=tk.W)
        self.doc_files_var = tk.StringVar()
        ttk.Entry(doc_frame, textvariable=self.doc_files_var, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(doc_frame, text="选择文档", command=self.browse_doc_files).grid(row=0, column=2)
        
        # 文档转换按钮
        doc_btn_frame = ttk.Frame(doc_frame)
        doc_btn_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(doc_btn_frame, text="CSV转Excel", command=self.csv_to_excel).pack(side=tk.LEFT, padx=10)
        ttk.Button(doc_btn_frame, text="Excel转CSV", command=self.excel_to_csv).pack(side=tk.LEFT, padx=10)
    
    def create_organize_tab(self):
        """创建文件整理标签页"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="📊 文件整理")
        
        # 按类型整理
        type_frame = ttk.LabelFrame(tab, text="按文件类型整理", padding="10")
        type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_frame, text="选择文件夹:").grid(row=0, column=0, sticky=tk.W)
        self.organize_folder = tk.StringVar()
        ttk.Entry(type_frame, textvariable=self.organize_folder, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(type_frame, text="浏览", command=lambda: self.browse_organize_folder("organize")).grid(row=0, column=2)
        
        ttk.Button(type_frame, text="开始整理文件", command=self.organize_by_type, 
                  style="Accent.TButton").grid(row=1, column=0, columnspan=3, pady=10)
        
        # 按日期整理
        date_frame = ttk.LabelFrame(tab, text="按修改日期整理", padding="10")
        date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_frame, text="选择文件夹:").grid(row=0, column=0, sticky=tk.W)
        self.date_folder = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.date_folder, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(date_frame, text="浏览", command=lambda: self.browse_organize_folder("date")).grid(row=0, column=2)
        
        ttk.Button(date_frame, text="按日期整理", command=self.organize_by_date).grid(row=1, column=0, columnspan=3, pady=10)
        
        # 重复文件查找
        duplicate_frame = ttk.LabelFrame(tab, text="重复文件查找", padding="10")
        duplicate_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(duplicate_frame, text="扫描文件夹:").grid(row=0, column=0, sticky=tk.W)
        self.duplicate_folder = tk.StringVar()
        ttk.Entry(duplicate_frame, textvariable=self.duplicate_folder, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(duplicate_frame, text="浏览", command=lambda: self.browse_organize_folder("duplicate")).grid(row=0, column=2)
        
        ttk.Button(duplicate_frame, text="查找重复文件", command=self.find_duplicates).grid(row=1, column=0, columnspan=3, pady=10)
    
    def create_log_area(self, parent):
        """创建日志显示区域"""
        log_frame = ttk.LabelFrame(parent, text="处理日志", padding="10")
        log_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=100, height=12, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 日志控制按钮
        log_btn_frame = ttk.Frame(log_frame)
        log_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(log_btn_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT)
        ttk.Button(log_btn_frame, text="导出日志", command=self.export_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_btn_frame, text="复制日志", command=self.copy_log).pack(side=tk.LEFT, padx=5)
    
    def browse_folder(self):
        """浏览文件夹"""
        folder = filedialog.askdirectory(title="选择工作目录")
        if folder:
            self.folder_path.set(folder)
            self.scan_files()
    
    def scan_files(self):
        """扫描文件夹中的文件"""
        folder = self.folder_path.get()
        if not folder or not os.path.exists(folder):
            return
        
        self.log_message(f"开始扫描文件夹: {folder}")
        
        # 在新线程中执行扫描
        thread = threading.Thread(target=self._scan_files_thread, args=(folder,))
        thread.daemon = True
        thread.start()
    
    def _scan_files_thread(self, folder):
        """在后台线程中扫描文件"""
        try:
            self.current_files = []
            
            for file_path in Path(folder).iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    file_info = {
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': self.format_file_size(stat.st_size),
                        'modified': file_path.stat().st_mtime
                    }
                    self.current_files.append(file_info)
            
            # 在GUI线程中更新显示
            self.root.after(0, self._update_file_list)
            self.root.after(0, lambda: self.log_message(f"扫描完成，找到 {len(self.current_files)} 个文件"))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"扫描错误: {str(e)}"))
    
    def _update_file_list(self):
        """更新文件列表显示"""
        # 清空现有列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # 添加新文件
        for file_info in self.current_files:
            self.file_tree.insert("", "end", values=(
                file_info['name'],
                file_info['size'],
                self.format_timestamp(file_info['modified'])
            ))
    
    def format_file_size(self, size_bytes):
        """格式化文件大小显示"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def format_timestamp(self, timestamp):
        """格式化时间戳"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def filter_files(self, event=None):
        """过滤文件"""
        self.scan_files()
    
    def refresh_files(self):
        """刷新文件列表"""
        self.scan_files()
    
    def browse_text_files(self):
        """浏览文本文件"""
        files = filedialog.askopenfilenames(
            title="选择文本文件",
            filetypes=[
                ("文本文件", "*.txt"),
                ("Python文件", "*.py"),
                ("配置文件", "*.ini *.conf *.json *.xml"),
                ("所有文件", "*.*")
            ]
        )
        if files:
            self.text_files_var.set(f"; ".join(files))
            self.text_listbox.delete(0, tk.END)
            for file in files:
                self.text_listbox.insert(tk.END, file)
            self.log_message(f"已选择 {len(files)} 个文本文件")
    
    def browse_image_files(self):
        """浏览图片文件"""
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff"),
                ("所有文件", "*.*")
            ]
        )
        if files:
            self.image_files_var.set(f"; ".join(files))
            self.image_listbox.delete(0, tk.END)
            for file in files:
                self.image_listbox.insert(tk.END, file)
            self.log_message(f"已选择 {len(files)} 个图片文件")
    
    def browse_doc_files(self):
        """浏览文档文件"""
        files = filedialog.askopenfilenames(
            title="选择文档文件",
            filetypes=[
                ("Excel文件", "*.xlsx *.xls"),
                ("CSV文件", "*.csv"),
                ("所有文件", "*.*")
            ]
        )
        if files:
            self.doc_files_var.set(f"; ".join(files))
            self.log_message(f"已选择 {len(files)} 个文档文件")
    
    def browse_organize_folder(self, folder_type):
        """浏览整理文件夹"""
        folder = filedialog.askdirectory(title="选择要整理的文件夹")
        if folder:
            if folder_type == "organize":
                self.organize_folder.set(folder)
            elif folder_type == "date":
                self.date_folder.set(folder)
            else:
                self.duplicate_folder.set(folder)
            self.log_message(f"已选择整理目录: {folder}")
    
    def preview_rename(self):
        """预览重命名"""
        if not self.current_files:
            messagebox.showwarning("警告", "请先选择文件夹并等待文件加载完成")
            return
        
        self.log_message("预览重命名功能开发中...")
        # 这里可以实现重命名预览逻辑
    
    def execute_rename(self):
        """执行重命名"""
        folder = self.folder_path.get()
        if not folder or not self.current_files:
            messagebox.showwarning("警告", "请先选择文件夹并等待文件加载完成")
            return
        
        selected_items = self.file_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要重命名的文件")
            return
        
        try:
            mode = self.rename_mode.get()
            count = 0
            
            for i, item in enumerate(selected_items):
                old_name = self.file_tree.item(item)['values'][0]
                old_path = os.path.join(folder, old_name)
                
                if mode == "pattern":
                    # 模式命名
                    pattern = self.name_pattern.get()
                    start_num = int(self.start_number.get())
                    new_name = pattern.replace("{序号}", str(start_num + i))
                    ext = os.path.splitext(old_name)[1]
                    new_name += ext
                    
                elif mode == "replace":
                    # 替换命名
                    find_text = self.find_text.get()
                    replace_text = self.replace_with.get()
                    name_part = os.path.splitext(old_name)[0]
                    ext = os.path.splitext(old_name)[1]
                    new_name = name_part.replace(find_text, replace_text) + ext
                    
                else:  # prefix mode
                    # 添加前后缀
                    prefix = self.prefix_text.get()
                    suffix = self.suffix_text.get()
                    name_part = os.path.splitext(old_name)[0]
                    ext = os.path.splitext(old_name)[1]
                    new_name = f"{prefix}{name_part}{suffix}{ext}"
                
                new_path = os.path.join(folder, new_name)
                
                # 执行重命名
                os.rename(old_path, new_path)
                count += 1
                self.log_message(f"重命名: {old_name} → {new_name}")
            
            messagebox.showinfo("成功", f"成功重命名 {count} 个文件")
            self.scan_files()  # 刷新文件列表
            
        except Exception as e:
            messagebox.showerror("错误", f"重命名失败: {str(e)}")
            self.log_message(f"重命名错误: {str(e)}")
    
    def undo_rename(self):
        """撤销重命名"""
        self.log_message("撤销功能开发中...")
    
    def preview_replace(self):
        """预览文本替换"""
        selected_files = self.text_listbox.get(0, tk.END)
        if not selected_files:
            messagebox.showwarning("警告", "请先选择要处理的文件")
            return
        
        self.log_message("文本替换预览功能开发中...")
    
    def execute_replace(self):
        """执行文本替换"""
        selected_files = self.text_listbox.get(0, tk.END)
        if not selected_files:
            messagebox.showwarning("警告", "请先选择要处理的文件")
            return
        
        find_text = self.text_find.get()
        if not find_text:
            messagebox.showwarning("警告", "请输入要查找的内容")
            return
        
        replace_text = self.text_replace.get()
        encoding = self.file_encoding.get()
        
        try:
            count = self.processor.batch_text_replace(
                selected_files, find_text, replace_text, encoding,
                self.case_sensitive.get(), self.use_regex.get()
            )
            
            messagebox.showinfo("成功", f"成功处理 {count} 个文件")
            self.log_message(f"文本替换完成: 处理了 {count} 个文件")
            
        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {str(e)}")
            self.log_message(f"文本替换错误: {str(e)}")
    
    def convert_images(self):
        """转换图片格式"""
        selected_files = self.image_listbox.get(0, tk.END)
        if not selected_files:
            messagebox.showwarning("警告", "请先选择要转换的图片")
            return
        
        target_format = self.target_format.get().lower()
        quality = int(self.quality.get())
        
        try:
            count = self.processor.convert_image_format(selected_files, target_format, quality)
            messagebox.showinfo("成功", f"成功转换 {count} 张图片")
            self.log_message(f"图片格式转换完成: 转换了 {count} 张图片到 {target_format.upper()} 格式")
            
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {str(e)}")
            self.log_message(f"图片转换错误: {str(e)}")
    
    def csv_to_excel(self):
        """CSV转Excel"""
        selected_files = filedialog.askopenfilenames(
            title="选择CSV文件",
            filetypes=[("CSV文件", "*.csv")]
        )
        
        if selected_files:
            try:
                count = self.processor.csv_to_excel(selected_files)
                messagebox.showinfo("成功", f"成功转换 {count} 个文件")
                self.log_message(f"CSV转Excel完成: 转换了 {count} 个文件")
            except Exception as e:
                messagebox.showerror("错误", f"转换失败: {str(e)}")
                self.log_message(f"CSV转Excel错误: {str(e)}")
    
    def excel_to_csv(self):
        """Excel转CSV"""
        selected_files = filedialog.askopenfilenames(
            title="选择Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls")]
        )
        
        if selected_files:
            try:
                count = self.processor.excel_to_csv(selected_files)
                messagebox.showinfo("成功", f"成功转换 {count} 个文件")
                self.log_message(f"Excel转CSV完成: 转换了 {count} 个文件")
            except Exception as e:
                messagebox.showerror("错误", f"转换失败: {str(e)}")
                self.log_message(f"Excel转CSV错误: {str(e)}")
    
    def organize_by_type(self):
        """按类型整理文件"""
        folder = self.organize_folder.get()
        if not folder:
            messagebox.showwarning("警告", "请先选择要整理的文件夹")
            return
        
        try:
            result = self.processor.organize_files_by_type(folder)
            messagebox.showinfo("成功", f"文件整理完成！\n创建了 {result['folders_created']} 个分类文件夹\n整理了 {result['files_moved']} 个文件")
            self.log_message(f"文件整理完成: 在 {folder} 中整理了 {result['files_moved']} 个文件")
            
        except Exception as e:
            messagebox.showerror("错误", f"整理失败: {str(e)}")
            self.log_message(f"文件整理错误: {str(e)}")
    
    def organize_by_date(self):
        """按日期整理文件"""
        folder = self.date_folder.get()
        if not folder:
            messagebox.showwarning("警告", "请先选择要整理的文件夹")
            return
        
        self.log_message("按日期整理功能开发中...")
    
    def find_duplicates(self):
        """查找重复文件"""
        folder = self.duplicate_folder.get()
        if not folder:
            messagebox.showwarning("警告", "请先选择要扫描的文件夹")
            return
        
        self.log_message("重复文件查找功能开发中...")
    
    def log_message(self, message):
        """添加日志消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete('1.0', tk.END)
    
    def export_log(self):
        """导出日志"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get('1.0', tk.END))
                self.log_message(f"日志已导出到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def copy_log(self):
        """复制日志到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.log_text.get('1.0', tk.END))
        self.log_message("日志已复制到剪贴板")
