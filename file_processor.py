"""
文件处理核心逻辑模块
File Processing Core Logic Module
"""

import os
import shutil
import pandas as pd
from PIL import Image
import re
from pathlib import Path

class FileProcessor:
    """文件处理器核心类"""
    
    def __init__(self):
        # 文件类型分类映射
        self.file_type_categories = {
            '图片': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg'],
            '文档': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.md'],
            '表格': ['.xls', '.xlsx', '.csv'],
            '演示文稿': ['.ppt', '.pptx'],
            '视频': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'],
            '音频': ['.mp3', '.wav', '.flac', '.aac', '.m4a'],
            '压缩包': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            '程序': ['.exe', '.msi', '.bat', '.sh', '.py', '.js', '.html', '.css'],
            '字体': ['.ttf', '.otf', '.woff', '.woff2'],
            '数据': ['.json', '.xml', '.sql', '.db', '.sqlite']
        }
    
    def batch_text_replace(self, file_paths, find_text, replace_text, encoding='utf-8', 
                          case_sensitive=False, use_regex=False):
        """
        批量文本替换
        
        Args:
            file_paths: 文件路径列表
            find_text: 要查找的文本
            replace_text: 替换文本
            encoding: 文件编码
            case_sensitive: 是否区分大小写
            use_regex: 是否使用正则表达式
            
        Returns:
            int: 成功处理的文件数量
        """
        count = 0
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                # 执行替换
                if use_regex:
                    if case_sensitive:
                        new_content = re.sub(find_text, replace_text, content)
                    else:
                        pattern = re.compile(find_text, re.IGNORECASE)
                        new_content = pattern.sub(replace_text, content)
                else:
                    if case_sensitive:
                        new_content = content.replace(find_text, replace_text)
                    else:
                        # 不区分大小写的普通替换
                        pattern = re.compile(re.escape(find_text), re.IGNORECASE)
                        new_content = pattern.sub(replace_text, content)
                
                # 写回文件
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(new_content)
                
                count += 1
                
            except Exception as e:
                raise Exception(f"处理文件 {file_path} 时出错: {str(e)}")
        
        return count
    
    def convert_image_format(self, image_paths, target_format, quality=85):
        """
        转换图片格式
        
        Args:
            image_paths: 图片路径列表
            target_format: 目标格式
            quality: 图片质量(1-100)
            
        Returns:
            int: 成功转换的图片数量
        """
        count = 0
        for image_path in image_paths:
            try:
                with Image.open(image_path) as img:
                    # 转换为RGB模式（JPG需要）
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # 新文件名
                    dir_name = os.path.dirname(image_path)
                    base_name = os.path.splitext(os.path.basename(image_path))[0]
                    new_path = os.path.join(dir_name, f"{base_name}.{target_format}")
                    
                    # 保存图片
                    img.save(new_path, format=target_format.upper(), quality=quality, optimize=True)
                    count += 1
                    
            except Exception as e:
                raise Exception(f"转换图片 {image_path} 时出错: {str(e)}")
        
        return count
    
    def csv_to_excel(self, csv_paths):
        """
        CSV转Excel
        
        Args:
            csv_paths: CSV文件路径列表
            
        Returns:
            int: 成功转换的文件数量
        """
        count = 0
        for csv_path in csv_paths:
            try:
                # 读取CSV
                df = pd.read_csv(csv_path)
                
                # 生成Excel文件名
                dir_name = os.path.dirname(csv_path)
                base_name = os.path.splitext(os.path.basename(csv_path))[0]
                excel_path = os.path.join(dir_name, f"{base_name}.xlsx")
                
                # 保存为Excel
                df.to_excel(excel_path, index=False)
                count += 1
                
            except Exception as e:
                raise Exception(f"转换CSV文件 {csv_path} 时出错: {str(e)}")
        
        return count
    
    def excel_to_csv(self, excel_paths):
        """
        Excel转CSV
        
        Args:
            excel_paths: Excel文件路径列表
            
        Returns:
            int: 成功转换的文件数量
        """
        count = 0
        for excel_path in excel_paths:
            try:
                # 读取Excel
                df = pd.read_excel(excel_path)
                
                # 生成CSV文件名
                dir_name = os.path.dirname(excel_path)
                base_name = os.path.splitext(os.path.basename(excel_path))[0]
                csv_path = os.path.join(dir_name, f"{base_name}.csv")
                
                # 保存为CSV
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                count += 1
                
            except Exception as e:
                raise Exception(f"转换Excel文件 {excel_path} 时出错: {str(e)}")
        
        return count
    
    def organize_files_by_type(self, folder_path):
        """
        按文件类型整理文件夹
        
        Args:
            folder_path: 要整理的文件夹路径
            
        Returns:
            dict: 整理结果统计
        """
        folder = Path(folder_path)
        if not folder.exists():
            raise Exception(f"文件夹不存在: {folder_path}")
        
        folders_created = 0
        files_moved = 0
        
        # 处理文件夹中的每个文件
        for file_path in folder.iterdir():
            if file_path.is_file():
                # 获取文件扩展名
                ext = file_path.suffix.lower()
                
                # 查找对应的分类
                category = '其他'
                for cat, extensions in self.file_type_categories.items():
                    if ext in extensions:
                        category = cat
                        break
                
                # 创建分类文件夹
                category_folder = folder / category
                if not category_folder.exists():
                    category_folder.mkdir()
                    folders_created += 1
                
                # 移动文件
                try:
                    new_path = category_folder / file_path.name
                    # 处理文件名冲突
                    counter = 1
                    while new_path.exists():
                        name_parts = file_path.stem, counter, file_path.suffix
                        new_name = f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                        new_path = category_folder / new_name
                        counter += 1
                    
                    shutil.move(str(file_path), str(new_path))
                    files_moved += 1
                    
                except Exception as e:
                    raise Exception(f"移动文件 {file_path.name} 时出错: {str(e)}")
        
        return {
            'folders_created': folders_created,
            'files_moved': files_moved
        }
    
    def get_file_info(self, file_path):
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            dict: 文件信息
        """
        path = Path(file_path)
        stat = path.stat()
        
        return {
            'name': path.name,
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'created': stat.st_ctime,
            'extension': path.suffix.lower(),
            'path': str(path)
        }
