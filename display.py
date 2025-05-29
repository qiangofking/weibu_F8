import tkinter as tk
import json
import sys
from tkinter import messagebox

def show_json_data(json_str):
    """显示JSON数据（支持多IP）"""
    try:
        data = json.loads(json_str)
        
        root = tk.Tk()
        root.title("威胁情报展示")
        root.resizable(True, True)  # 允许调整窗口大小
        root.attributes('-alpha', 0.85)
        root.attributes('-topmost', True)
        root.attributes('-toolwindow', 1)
        
        # 创建滚动条容器
        container = tk.Frame(root)
        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        # 配置滚动区域和滚轮支持
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        container.pack(fill="both", expand=True)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 获取鼠标位置（跨平台）
        if sys.platform == 'win32':
            import ctypes
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            pt = POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            x, y = pt.x, pt.y
        else:
            x, y = 100, 100
            
        root.geometry(f"+{int(x)+10}+{int(y)+10}")
        
        row = 0
        for i, result in enumerate(data['results']):
            # 显示分隔线和查询IP(带序号)
            row += 1
            
            # 显示结果字段
            for key in ['ip', 'severity', 'judgments', 'is_malicious', 'location']:
                if key in result:
                    # 特殊处理"IP"字段
                    if key == 'ip':
                        tk.Label(scrollable_frame, text=f"{i+1}. 查询IP: {result['ip']}", 
                                font=('Arial', 10, 'bold'), fg='blue').grid(row=row, column=0, columnspan=2, sticky='w')
                    # 特殊处理"是否恶意"字段
                    elif key == 'is_malicious' and str(result[key]).lower() == 'true':
                        tk.Label(scrollable_frame, text=f"是否恶意:{result[key]}", font=('Arial', 10), 
                                bg='#ffcccc').grid(row=row, column=1, sticky='w')
                    else:
                        tk.Label(scrollable_frame, text=f"{key}：{result[key]}", font=('Arial', 10)).grid(row=row, column=1, sticky='w')
                    row += 1
            
            # 添加分隔线（最后一个不添加）
            if i < len(data['results']) - 1:
                tk.Frame(scrollable_frame, height=1, bg='gray').grid(row=row, column=0, columnspan=2, sticky='we', pady=5)
                row += 1
                    
        # 绑定ESC键关闭窗口
        root.bind('<Escape>', lambda e: root.destroy())
        root.protocol("WM_DELETE_WINDOW", root.destroy)
        
        # 计算窗口高度（每行约20像素，最大17行）
        line_height = 20
        max_height = min(row, 17) * line_height + 20
        root.geometry(f"400x{max_height}+{int(x)+10}+{int(y)+10}")
        
        # 初始焦点设置,可滚轮
        scrollable_frame.focus_set()
        root.mainloop()
    except Exception as e:
        messagebox.showerror("错误", f"解析JSON失败: {str(e)}")

if __name__ == "__main__":
    if not sys.stdin.isatty():  # 检查是否有管道输入
        json_str = sys.stdin.read()
        show_json_data(json_str)
    else:
        messagebox.showwarning("提示", "请通过管道传入JSON数据")
