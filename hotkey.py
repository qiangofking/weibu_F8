import os
import time
from pynput import keyboard
import subprocess
import sys
import pyperclip
import re
import concurrent.futures
import json

def get_selected_text():
    """跨平台获取选中文本（最终优化版）"""
    try:
        print(f"[{time.ctime()}] 开始获取选中文本")  # 带时间戳的调试
        try:
            import win32clipboard
            import win32con
            
            # 清空剪贴板
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
            
            # 模拟Ctrl+C
            import ctypes
            ctypes.windll.user32.keybd_event(0x11, 0, 0, 0)  # Ctrl
            ctypes.windll.user32.keybd_event(0x43, 0, 0, 0)  # C
            time.sleep(0.05)  # 短暂延迟
            ctypes.windll.user32.keybd_event(0x43, 0, 0x0002, 0)  # C up
            ctypes.windll.user32.keybd_event(0x11, 0, 0x0002, 0)  # Ctrl up
            
            time.sleep(0.3)  # 确保复制完成
            
            win32clipboard.OpenClipboard()
            try:
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                print(f"[{time.ctime()}] 获取到文本: {text[:50]}...")  # 截断长文本
            finally:
                win32clipboard.CloseClipboard()
                
            return text if text else ""
            
        except ImportError:
            print("提示: 安装pywin32可提高剪贴板可靠性 (pip install pywin32)")
            return pyperclip.paste()
                
    except Exception as e:
        print(f"获取选中文本出错: {str(e)}")
        return ""

import concurrent.futures
import threading

# 预加载模块路径
script_dir = os.path.dirname(os.path.abspath(__file__))
query_path = os.path.join(script_dir, 'query.py')
display_path = os.path.join(script_dir, 'display.py')

def query_ip(ip):
    """执行IP查询并返回结果"""
    print(f"[{time.ctime()}] 开始查询IP: {ip}")
    
    result = subprocess.run(
        [sys.executable, query_path, ip],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    print(f"[{time.ctime()}] 查询完成 - IP: {ip} | 返回码: {result.returncode}")
    return result.stdout if result.returncode == 0 else ""

def on_press(key):
    try:
        if key == keyboard.Key.f8:
            print("[DEBUG] F8按键触发")  # 调试输出
            # 使用线程池并行处理
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # 获取选中文本
                selected_text = get_selected_text()
                print(f"[DEBUG] 获取选中文本: {selected_text}")  # 调试输出
                # 提取IP地址（支持多种分隔符）
                ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
                ip_list = re.findall(ip_pattern, selected_text.replace('，', ',').replace('\n', ','))
                
                if ip_list:
                    print(f"[DEBUG] 提取到IP列表: {ip_list}")
                    
                    # 查询所有IP并保持顺序
                    results = []
                    for ip in ip_list:
                        print(f"[DEBUG] 正在查询IP: {ip}")
                        result = executor.submit(query_ip, ip).result()
                        if result:
                            try:
                                data = json.loads(result)
                                results.append(data)
                            except json.JSONDecodeError:
                                print(f"错误: IP {ip} 的查询结果格式无效")
                    
                    if results:
                        # 合并所有结果
                        combined_result = {
                            'results': results
                        }
                        print(f"[DEBUG] 合并查询结果: {combined_result}")
                        print("[DEBUG] 准备显示合并查询结果")
                        
                        # 在独立线程中显示结果
                        def show_result():
                            try:
                                p = subprocess.Popen(
                                    [sys.executable, display_path],
                                    stdin=subprocess.PIPE,
                                    text=True
                                )
                                p.communicate(input=json.dumps(combined_result))
                            except Exception as e:
                                print(f"显示结果出错: {str(e)}")
                        
                        threading.Thread(target=show_result, daemon=True).start()
                    else:
                        print("警告: 所有IP查询均未返回有效结果")
                else:
                    print("未在选中文本中找到IP地址")
    except Exception as e:
        print(f"处理错误: {str(e)}")

def on_release(key):
    if key == keyboard.Key.esc:
        # ESC键不终止主进程，只用于关闭显示窗口
        pass

# 启动监听
import signal
import sys
import threading

def signal_handler(sig, frame):
    print("\n正在退出监听服务...")
    os._exit(0)  # 强制退出

if __name__ == "__main__":
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    
    # 在独立线程中运行监听器
    def run_listener():
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    listener_thread = threading.Thread(target=run_listener, daemon=True)
    listener_thread.start()

    print("全局快捷键监听已启动，按F8查询选中IP的威胁情报，Ctrl+C退出...")
    
    # 主线程等待退出信号
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在退出监听服务...")
        sys.exit(0)
