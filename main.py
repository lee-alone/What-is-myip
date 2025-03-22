import tkinter as tk
from tkinter import ttk
import json
import asyncio
import threading
from network_utils import check_all_ips
from ip_utils import get_local_ips
from config import DEFAULT_API_ENDPOINTS, load_custom_endpoints

class IPCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP地址查询器")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f5f6fa')
        
        # 设置主题样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置全局字体
        default_font = ('微软雅黑', 10)
        title_font = ('微软雅黑', 12, 'bold')
        
        # 设置Notebook样式
        style.configure('TNotebook', background='#f5f6fa', borderwidth=0)
        style.configure('TNotebook.Tab', padding=[12, 8], font=default_font, background='#f5f6fa')
        style.map('TNotebook.Tab',
                  background=[('selected', '#ffffff'), ('!selected', '#f5f6fa')],
                  foreground=[('selected', '#2d3436'), ('!selected', '#636e72')])
        
        # 设置Frame样式
        style.configure('TFrame', background='#ffffff', borderwidth=1, relief='solid')
        
        # 设置Button样式
        style.configure('TButton',
                      padding=[20, 10],
                      relief='flat',
                      font=default_font,
                      background='#0984e3',
                      foreground='white')
        style.map('TButton',
                  background=[('active', '#74b9ff'), ('pressed', '#0652DD')],
                  foreground=[('pressed', 'white')])
        
        # 设置Treeview样式
        style.configure('Treeview',
                      background='white',
                      fieldbackground='white',
                      rowheight=40,
                      font=default_font)
        style.configure('Treeview.Heading',
                      font=title_font,
                      background='#f5f6fa',
                      foreground='#2d3436',
                      relief='flat')
        style.map('Treeview',
                  background=[('selected', '#74b9ff')],
                  foreground=[('selected', 'white')])
        
        # 设置状态栏样式
        style.configure('Status.TLabel',
                      padding=10,
                      background='#f5f6fa',
                      font=default_font)
        
        # 创建状态栏
        self.status_bar = ttk.Label(root, text="", style='Status.TLabel', anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建notebook用于分页显示
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # 外网IP查询页
        self.external_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.external_frame, text='外网IP')
        
        # 本地IP查询页
        self.local_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.local_frame, text='本地IP')
        
        self.setup_external_ip_frame()
        self.setup_local_ip_frame()
        
        # 加载自定义API端点
        self.api_endpoints = DEFAULT_API_ENDPOINTS
        self.load_custom_endpoints()
        
        # 创建事件循环
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # 在新线程中运行事件循环
        def run_event_loop():
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        
        self.loop_thread = threading.Thread(target=run_event_loop, daemon=True)
        self.loop_thread.start()
        
        # 初始查询
        self.root.after(100, self.check_external_ip)
        self.check_local_ip()

    def setup_external_ip_frame(self):
        # 添加标签
        header_frame = ttk.Frame(self.external_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        external_label = ttk.Label(header_frame, text="外网IP查询结果", font=('微软雅黑', 12, 'bold'))
        external_label.pack(side=tk.LEFT)

        # 创建表格
        self.tree = ttk.Treeview(self.external_frame, columns=('服务器名称', '服务器IP', '服务器信息'), show='headings')
        self.tree.heading('服务器名称', text='服务器名称')
        self.tree.heading('服务器IP', text='服务器IP')
        self.tree.heading('服务器信息', text='服务器信息')
        self.tree.column('服务器名称', width=200)
        self.tree.column('服务器IP', width=200)
        self.tree.column('服务器信息', width=300)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.external_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill='both')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=5)

        # 重试按钮
        retry_btn = ttk.Button(self.external_frame, text="重新检查", command=self.check_external_ip)
        retry_btn.pack(pady=10)

    def setup_local_ip_frame(self):
        # 添加标签
        header_frame = ttk.Frame(self.local_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        local_label = ttk.Label(header_frame, text="本地IP地址", font=('微软雅黑', 12, 'bold'))
        local_label.pack(side=tk.LEFT)

        # 创建文本框和滚动条
        text_frame = ttk.Frame(self.local_frame)
        text_frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        self.local_ip_text = tk.Text(text_frame, height=15, width=60, font=('微软雅黑', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.local_ip_text.yview)
        self.local_ip_text.configure(yscrollcommand=scrollbar.set)
        
        self.local_ip_text.pack(side=tk.LEFT, expand=True, fill='both')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        refresh_btn = ttk.Button(self.local_frame, text="刷新", command=self.check_local_ip)
        refresh_btn.pack(pady=10)

    async def async_check_external_ip(self):
        self.status_bar.config(text="正在查询外网IP...")
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)

        async def process_results():
            results = []
            async for result in check_all_ips(self.api_endpoints):
                results.append(result)
                self.status_bar.config(text=f"正在查询 {result['name']}...")
            
            for result in results:
                self.tree.insert('', tk.END, values=(result['name'], result['ip'], result['server']))
            
            self.status_bar.config(text="外网IP查询完成")

        asyncio.run_coroutine_threadsafe(process_results(), self.loop)

    def check_external_ip(self):
        # 移除 future.result(timeout=10) 调用，因为它会阻塞事件循环
        asyncio.run_coroutine_threadsafe(self.async_check_external_ip(), self.loop)


    def check_local_ip(self):
        self.local_ip_text.delete(1.0, tk.END)
        self.status_bar.config(text="正在查询本地IP...")
        self.root.update()
        
        ips = get_local_ips()
        self.local_ip_text.insert(tk.END, "本机IP地址：\n\n")
        for adapter, ip in ips.items():
            self.local_ip_text.insert(tk.END, f"{adapter}: {ip}\n")
            
        self.status_bar.config(text="本地IP查询完成")

    def load_custom_endpoints(self):
        try:
            custom_endpoints = load_custom_endpoints()
            if custom_endpoints:
                self.api_endpoints.extend(custom_endpoints)
        except Exception as e:
            print(f"加载自定义端点失败: {str(e)}")

    def on_closing(self):
        self.loop.stop()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = IPCheckerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
