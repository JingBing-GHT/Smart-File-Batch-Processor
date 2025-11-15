#!/usr/bin/env python3
"""
智能文件批量处理工具 - 主程序入口
Smart File Batch Processor - Main Entry Point
"""

import tkinter as tk
from gui_interface import FileProcessorGUI

def main():
    """主程序入口函数"""
    try:
        # 创建主窗口
        root = tk.Tk()
        
        # 设置窗口标题和图标
        root.title("智能文件批量处理工具 v2.0")
        root.geometry("1000x750")
        
        # 设置窗口最小尺寸
        root.minsize(900, 700)
        
        # 创建主应用程序
        app = FileProcessorGUI(root)
        
        # 启动主循环
        root.mainloop()
        
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()
