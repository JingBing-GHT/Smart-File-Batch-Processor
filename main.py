import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
from pathlib import Path
import pandas as pd
from PIL import Image
import shutil
import re


class FileProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("智能文件批量处理工具 v2.0")
        self.root.geometry("900x700")
        self.current_files = []
        self.create_widgets()

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标签页控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # 批量重命名标签页
        rename_frame = ttk.Frame(notebook, padding="10")
        self.create_rename_tab(rename_frame)
        notebook.add(rename_frame, text="📁 批量重命名")

        # 查找替换标签页
        find_replace_frame = ttk.Frame(notebook, padding="10")
        self.create_find_replace_tab(find_replace_frame)
        notebook.add(find_replace_frame, text="🔍 文本替换")

        # 格式转换标签页
        convert_frame = ttk.Frame(notebook, padding="10")
        self.create_convert_tab(convert_frame)
        notebook.add(convert_frame, text="🔄 格式转换")

        # 文件整理标签页
        organize_frame = ttk.Frame(notebook, padding="10")
        self.create_organize_tab(organize_frame)
        notebook.add(organize_frame, text="📊 文件整理")

        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="5")
        log_frame.pack(fill=tk.X, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, width=100, height=12)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def create_rename_tab(self, parent):
        # 文件选择区域
        select_frame = ttk.LabelFrame(parent, text="文件选择", padding="5")
        select_frame.pack(fill=tk.X, pady=5)

        ttk.Label(select_frame, text="选择文件夹:").grid(row=0, column=0, sticky=tk.W)
        self.folder_path = tk.StringVar()
        ttk.Entry(select_frame, textvariable=self.folder_path, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(select_frame, text="浏览文件夹", command=self.browse_folder).grid(row=0, column=2)
        ttk.Button(select_frame, text="刷新文件列表", command=self.refresh_files).grid(row=0, column=3, padx=5)

        # 文件类型过滤
        ttk.Label(select_frame, text="文件类型:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.file_type = ttk.Combobox(select_frame, values=["所有文件", "图片文件", "文档文件", "视频文件", "音频文件"],
                                      width=15)
        self.file_type.set("所有文件")
        self.file_type.grid(row=1, column=1, sticky=tk.W, padx=5)
        self.file_type.bind('<<ComboboxSelected>>', self.filter_files)

        # 文件列表
        list_frame = ttk.LabelFrame(parent, text="文件列表", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=8)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # 重命名规则区域
        rule_frame = ttk.LabelFrame(parent, text="重命名规则", padding="5")
        rule_frame.pack(fill=tk.X, pady=5)

        # 命名模式选择
        ttk.Label(rule_frame, text="命名模式:").grid(row=0, column=0, sticky=tk.W)
        self.rename_mode = tk.StringVar(value="pattern")
        ttk.Radiobutton(rule_frame, text="模式命名", variable=self.rename_mode, value="pattern").grid(row=0, column=1,
                                                                                                      sticky=tk.W)
        ttk.Radiobutton(rule_frame, text="替换命名", variable=self.rename_mode, value="replace").grid(row=0, column=2,
                                                                                                      sticky=tk.W)
        ttk.Radiobutton(rule_frame, text="添加前后缀", variable=self.rename_mode, value="prefix").grid(row=0, column=3,
                                                                                                       sticky=tk.W)

        # 模式命名
        pattern_frame = ttk.Frame(rule_frame)
        pattern_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=5)
        ttk.Label(pattern_frame, text="命名模板:").pack(side=tk.LEFT)
        self.name_pattern = ttk.Entry(pattern_frame, width=30)
        self.name_pattern.insert(0, "文件_{序号}")
        self.name_pattern.pack(side=tk.LEFT, padx=5)
        ttk.Label(pattern_frame, text="起始序号:").pack(side=tk.LEFT)
        self.start_number = ttk.Spinbox(pattern_frame, from_=1, to=10000, width=8)
        self.start_number.set(1)
        self.start_number.pack(side=tk.LEFT, padx=5)

        # 替换命名
        replace_frame = ttk.Frame(rule_frame)
        replace_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=5)
        ttk.Label(replace_frame, text="查找:").pack(side=tk.LEFT)
        self.find_text = ttk.Entry(replace_frame, width=20)
        self.find_text.pack(side=tk.LEFT, padx=2)
        ttk.Label(replace_frame, text="替换为:").pack(side=tk.LEFT)
        self.replace_with = ttk.Entry(replace_frame, width=20)
        self.replace_with.pack(side=tk.LEFT, padx=2)

        # 添加前后缀
        prefix_frame = ttk.Frame(rule_frame)
        prefix_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=5)
        ttk.Label(prefix_frame, text="前缀:").pack(side=tk.LEFT)
        self.prefix_text = ttk.Entry(prefix_frame, width=15)
        self.prefix_text.pack(side=tk.LEFT, padx=2)
        ttk.Label(prefix_frame, text="后缀:").pack(side=tk.LEFT)
        self.suffix_text = ttk.Entry(prefix_frame, width=15)
        self.suffix_text.pack(side=tk.LEFT, padx=2)

        # 执行按钮
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="预览重命名结果", command=self.preview_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="执行重命名", command=self.execute_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="撤销上次操作", command=self.undo_rename).pack(side=tk.LEFT, padx=5)

    def create_find_replace_tab(self, parent):
        # 文件选择
        select_frame = ttk.LabelFrame(parent, text="文件选择", padding="5")
        select_frame.pack(fill=tk.X, pady=5)

        ttk.Label(select_frame, text="选择文件:").grid(row=0, column=0, sticky=tk.W)
        self.text_files = tk.StringVar()
        ttk.Entry(select_frame, textvariable=self.text_files, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(select_frame, text="选择文件", command=self.browse_text_files).grid(row=0, column=2)

        # 文本文件列表
        self.text_listbox = tk.Listbox(select_frame, selectmode=tk.EXTENDED, height=4)
        self.text_listbox.grid(row=1, column=0, columnspan=3, sticky=tk.W + tk.E, pady=5)
        select_frame.columnconfigure(1, weight=1)

        # 查找替换规则
        rule_frame = ttk.LabelFrame(parent, text="查找替换规则", padding="5")
        rule_frame.pack(fill=tk.X, pady=5)

        ttk.Label(rule_frame, text="查找内容:").grid(row=0, column=0, sticky=tk.W)
        self.text_find = ttk.Entry(rule_frame, width=40)
        self.text_find.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(rule_frame, text="替换为:").grid(row=1, column=0, sticky=tk.W)
        self.text_replace = ttk.Entry(rule_frame, width=40)
        self.text_replace.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(rule_frame, text="文件编码:").grid(row=2, column=0, sticky=tk.W)
        self.file_encoding = ttk.Combobox(rule_frame, values=["utf-8", "gbk", "gb2312", "ascii"], width=15)
        self.file_encoding.set("utf-8")
        self.file_encoding.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        # 选项
        options_frame = ttk.Frame(rule_frame)
        options_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.case_sensitive = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="区分大小写", variable=self.case_sensitive).pack(side=tk.LEFT, padx=5)
        self.whole_word = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="全字匹配", variable=self.whole_word).pack(side=tk.LEFT, padx=5)
        self.use_regex = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="使用正则表达式", variable=self.use_regex).pack(side=tk.LEFT, padx=5)

        # 执行按钮
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="预览替换", command=self.preview_replace).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="执行替换", command=self.execute_replace).pack(side=tk.LEFT, padx=5)

    def create_convert_tab(self, parent):
        # 图片格式转换
        img_frame = ttk.LabelFrame(parent, text="图片格式转换", padding="5")
        img_frame.pack(fill=tk.X, pady=5)

        ttk.Label(img_frame, text="选择图片文件:").grid(row=0, column=0, sticky=tk.W)
        self.image_files = tk.StringVar()
        ttk.Entry(img_frame, textvariable=self.image_files, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(img_frame, text="选择图片", command=self.browse_image_files).grid(row=0, column=2)

        # 图片列表
        self.image_listbox = tk.Listbox(img_frame, selectmode=tk.EXTENDED, height=4)
        self.image_listbox.grid(row=1, column=0, columnspan=3, sticky=tk.W + tk.E, pady=5)
        img_frame.columnconfigure(1, weight=1)

        # 转换设置
        convert_settings = ttk.Frame(img_frame)
        convert_settings.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)

        ttk.Label(convert_settings, text="目标格式:").pack(side=tk.LEFT)
        self.target_format = ttk.Combobox(convert_settings, values=["JPG", "PNG", "WEBP", "BMP", "TIFF"], width=10)
        self.target_format.set("JPG")
        self.target_format.pack(side=tk.LEFT, padx=5)

        ttk.Label(convert_settings, text="质量(1-100):").pack(side=tk.LEFT)
        self.quality = ttk.Spinbox(convert_settings, from_=1, to=100, width=8)
        self.quality.set(85)
        self.quality.pack(side=tk.LEFT, padx=5)

        ttk.Button(convert_settings, text="转换图片格式", command=self.convert_images).pack(side=tk.LEFT, padx=20)

        # 文档转换区域
        doc_frame = ttk.LabelFrame(parent, text="文档格式转换", padding="5")
        doc_frame.pack(fill=tk.X, pady=5)

        ttk.Label(doc_frame, text="选择文档文件:").grid(row=0, column=0, sticky=tk.W)
        self.doc_files = tk.StringVar()
        ttk.Entry(doc_frame, textvariable=self.doc_files, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(doc_frame, text="选择文档", command=self.browse_doc_files).grid(row=0, column=2)

        ttk.Button(doc_frame, text="CSV转Excel", command=self.csv_to_excel).grid(row=1, column=0, pady=5)
        ttk.Button(doc_frame, text="Excel转CSV", command=self.excel_to_csv).grid(row=1, column=1, pady=5)

    def create_organize_tab(self, parent):
        # 按类型整理
        type_frame = ttk.LabelFrame(parent, text="按文件类型整理", padding="5")
        type_frame.pack(fill=tk.X, pady=5)

        ttk.Label(type_frame, text="选择文件夹:").grid(row=0, column=0, sticky=tk.W)
        self.organize_folder = tk.StringVar()
        ttk.Entry(type_frame, textvariable=self.organize_folder, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(type_frame, text="浏览", command=lambda: self.browse_organize_folder(type_frame)).grid(row=0,
                                                                                                          column=2)

        ttk.Button(type_frame, text="按类型创建文件夹并整理", command=self.organize_by_type).grid(row=1, column=0,
                                                                                                  columnspan=3, pady=10)

        # 按日期整理
        date_frame = ttk.LabelFrame(parent, text="按修改日期整理", padding="5")
        date_frame.pack(fill=tk.X, pady=5)

        ttk.Label(date_frame, text="选择文件夹:").grid(row=0, column=0, sticky=tk.W)
        self.date_folder = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.date_folder, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(date_frame, text="浏览", command=lambda: self.browse_organize_folder(date_frame)).grid(row=0,
                                                                                                          column=2)

        ttk.Button(date_frame, text="按年月创建文件夹并整理", command=self.organize_by_date).grid(row=1, column=0,
                                                                                                  columnspan=3, pady=10)

        # 重复文件查找
        duplicate_frame = ttk.LabelFrame(parent, text="重复文件查找", padding="5")
        duplicate_frame.pack(fill=tk.X, pady=5)

        ttk.Label(duplicate_frame, text="扫描文件夹:").grid(row=0, column=0, sticky=tk.W)
        self.duplicate_folder = tk.StringVar()
        ttk.Entry(duplicate_frame, textvariable=self.duplicate_folder, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(duplicate_frame, text="浏览", command=lambda: self.browse_organize_folder(duplicate_frame)).grid(
            row=0, column=2)

        ttk.Button(duplicate_frame, text="查找重复文件", command=self.find_duplicates).grid(row=1, column=0,
                                                                                            columnspan=3, pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.scan_files()

    def scan_files(self):
        folder = self.folder_path.get()
        if not folder or not os.path.exists(folder):
            return

        self.current_files = []
        self.file_listbox.delete(0, tk.END)

        try:
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    self.current_files.append(file)
                    self.file_listbox.insert(tk.END, file)

            self.log_message(f"扫描完成，找到 {len(self.current_files)} 个文件")
        except Exception as e:
            self.log_message(f"扫描错误: {str(e)}")

    def filter_files(self, event=None):
        # 简化实现：重新扫描文件
        self.scan_files()

    def refresh_files(self):
        self.scan_files()

    def browse_text_files(self):
        files = filedialog.askopenfilenames(
            title="选择文本文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if files:
            self.text_files.set("; ".join(files))
            self.text_listbox.delete(0, tk.END)
            for file in files:
                self.text_listbox.insert(tk.END, file)

    def browse_image_files(self):
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"), ("所有文件", "*.*")]
        )
        if files:
            self.image_files.set("; ".join(files))
            self.image_listbox.delete(0, tk.END)
            for file in files:
                self.image_listbox.insert(tk.END, file)

    def browse_doc_files(self):
        files = filedialog.askopenfilenames(
            title="选择文档文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if files:
            self.doc_files.set("; ".join(files))

    def browse_organize_folder(self, parent_frame):
        folder = filedialog.askdirectory()
        if folder:
            # 根据父框架更新对应的StringVar
            if "organize_folder" in str(parent_frame):
                self.organize_folder.set(folder)
            elif "date_folder" in str(parent_frame):
                self.date_folder.set(folder)
            else:
                self.duplicate_folder.set(folder)

    def preview_rename(self):
        self.log_message("预览重命名功能开发中...")

    def execute_rename(self):
        folder = self.folder_path.get()
        if not folder or not self.current_files:
            messagebox.showwarning("警告", "请先选择文件夹并等待文件加载完成")
            return

        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "请先选择要重命名的文件")
            return

        try:
            mode = self.rename_mode.get()
            count = 0

            for i, index in enumerate(selected_indices):
                old_name = self.current_files[index]
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
                os.rename(old_path, new_path)
                count += 1
                self.log_message(f"重命名: {old_name} -> {new_name}")

            messagebox.showinfo("成功", f"成功重命名 {count} 个文件")
            self.scan_files()  # 刷新文件列表

        except Exception as e:
            messagebox.showerror("错误", f"重命名失败: {str(e)}")

    def undo_rename(self):
        self.log_message("撤销功能开发中...")

    def preview_replace(self):
        self.log_message("预览替换功能开发中...")

    def execute_replace(self):
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
            count = 0
            for file_path in selected_files:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()

                # 执行替换
                if self.use_regex.get():
                    new_content = re.sub(find_text, replace_text, content)
                else:
                    if self.case_sensitive.get():
                        new_content = content.replace(find_text, replace_text)
                    else:
                        pattern = re.compile(re.escape(find_text), re.IGNORECASE)
                        new_content = pattern.sub(replace_text, content)

                # 写回文件
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(new_content)

                count += 1
                self.log_message(f"处理完成: {os.path.basename(file_path)}")

            messagebox.showinfo("成功", f"成功处理 {count} 个文件")

        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {str(e)}")

    def convert_images(self):
        selected_files = self.image_listbox.get(0, tk.END)
        if not selected_files:
            messagebox.showwarning("警告", "请先选择要转换的图片")
            return

        target_format = self.target_format.get().lower()
        quality = int(self.quality.get())

        try:
            count = 0
            for file_path in selected_files:
                try:
                    with Image.open(file_path) as img:
                        # 转换为RGB模式（JPG需要）
                        if img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')

                        # 新文件名
                        dir_name = os.path.dirname(file_path)
                        base_name = os.path.splitext(os.path.basename(file_path))[0]
                        new_path = os.path.join(dir_name, f"{base_name}.{target_format}")

                        # 保存图片
                        img.save(new_path, format=target_format.upper(), quality=quality, optimize=True)
                        count += 1
                        self.log_message(f"转换成功: {os.path.basename(file_path)} -> {os.path.basename(new_path)}")

                except Exception as e:
                    self.log_message(f"转换失败 {os.path.basename(file_path)}: {str(e)}")

            messagebox.showinfo("成功", f"成功转换 {count} 张图片")

        except Exception as e:
            messagebox.showerror("错误", f"转换过程出错: {str(e)}")

    def csv_to_excel(self):
        self.log_message("CSV转Excel功能开发中...")

    def excel_to_csv(self):
        self.log_message("Excel转CSV功能开发中...")

    def organize_by_type(self):
        folder = self.organize_folder.get()
        if not folder:
            messagebox.showwarning("警告", "请先选择要整理的文件夹")
            return

        try:
            # 文件类型映射
            type_folders = {
                '图片': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
                '文档': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
                '表格': ['.xls', '.xlsx', '.csv'],
                '视频': ['.mp4', '.avi', '.mov', '.wmv', '.flv'],
                '音频': ['.mp3', '.wav', '.flac', '.aac'],
                '压缩包': ['.zip', '.rar', '.7z', '.tar', '.gz'],
                '程序': ['.exe', '.msi', '.bat', '.sh', '.py']
            }

            count = 0
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file)[1].lower()

                    # 查找对应的分类
                    found = False
                    for category, extensions in type_folders.items():
                        if ext in extensions:
                            category_folder = os.path.join(folder, category)
                            os.makedirs(category_folder, exist_ok=True)
                            shutil.move(file_path, os.path.join(category_folder, file))
                            count += 1
                            found = True
                            break

                    if not found:
                        # 未分类文件
                        other_folder = os.path.join(folder, '其他')
                        os.makedirs(other_folder, exist_ok=True)
                        shutil.move(file_path, os.path.join(other_folder, file))
                        count += 1

            self.log_message(f"文件整理完成，共整理 {count} 个文件")
            messagebox.showinfo("成功", f"文件整理完成！共整理 {count} 个文件")

        except Exception as e:
            messagebox.showerror("错误", f"整理失败: {str(e)}")

    def organize_by_date(self):
        self.log_message("按日期整理功能开发中...")

    def find_duplicates(self):
        self.log_message("查找重复文件功能开发中...")

    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()


def main():
    root = tk.Tk()
    app = FileProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
