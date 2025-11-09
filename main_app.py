# main_app.py

import tkinter as tk
from tkinter import ttk
import threading
from src.network_client import ApiClient
import src.config as config
from colorama import init

# 导入新模块
from src.activity_fetcher import ActivityFetcher, ActivityFetcherThread
from src.ui_manager import UIManager

# Initialize colorama for cross-platform color support
init(autoreset=True)

class ActivityViewer(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("中国石油大学第二课堂活动查询助手")
        self.geometry("1200x700")

        self.client = ApiClient()
        # 存储所有活动数据的列表，用于排序和按需加载
        self.activity_data_cache = []
        # 存储学生姓名
        self.student_name = None

        # 初始化活动获取器
        self.fetcher = ActivityFetcher(self.client, config.DETAIL_FETCH_LIMIT)
        self.fetcher_thread = None

        # 设置专业主题
        style = ttk.Style(self)
        style.theme_use('default')
        style.configure("Treeview", rowheight=25)

        # --- Login Frame ---
        login_frame = ttk.Frame(self, padding="10")
        login_frame.pack(fill='x')

        ttk.Label(login_frame, text="学号:").pack(side='left', padx=(0, 5))
        self.user_entry = ttk.Entry(login_frame, width=20)
        self.user_entry.pack(side='left', padx=5)

        ttk.Label(login_frame, text="密码:").pack(side='left', padx=(10, 5))
        self.pass_entry = ttk.Entry(login_frame, show="*", width=20)
        self.pass_entry.pack(side='left', padx=5)

        self.login_button = ttk.Button(login_frame, text="登录", command=self.perform_login)
        self.login_button.pack(side='left', padx=5)

        self.fetch_button = ttk.Button(login_frame, text="获取活动列表", command=self.start_data_fetch, state="disabled")
        self.fetch_button.pack(side='left', padx=5)

        # --- Status Bar ---
        self.status_var = tk.StringVar()
        self.status_var.set("请先登录")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief='sunken', anchor='w', padding="5")
        status_bar.pack(side='bottom', fill='x')

        # --- Treeview (Table) Frame ---
        tree_frame = ttk.Frame(self, padding="10")
        tree_frame.pack(expand=True, fill='both')

        columns = ('name', 'time', 'duration', 'points', 'signin', 'signout', 'tags')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        # Define Headings and Column Widths
        self.tree.heading('name', text='活动名称')
        self.tree.column('name', width=300, anchor='w')
        self.tree.heading('time', text='活动时间')
        self.tree.column('time', width=150, anchor='c')
        self.tree.heading('duration', text='持续时间')
        self.tree.column('duration', width=80, anchor='c')
        self.tree.heading('points', text='积分')
        self.tree.column('points', width=80, anchor='c')
        self.tree.heading('signin', text='签到情况')
        self.tree.column('signin', width=120, anchor='c')
        self.tree.heading('signout', text='签退情况')
        self.tree.column('signout', width=120, anchor='c')
        self.tree.heading('tags', text='标签')
        self.tree.column('tags', width=200, anchor='w')

        # Add Scrollbars
        ysb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)

        ysb.pack(side='right', fill='y')
        xsb.pack(side='bottom', fill='x')
        self.tree.pack(expand=True, fill='both')

        # 初始化UI管理器
        self.ui_manager = UIManager(self, self.tree)

        # 绑定双击事件，用于按需加载详情
        self.tree.bind('<Double-1>', self.fetch_detail_on_double_click)


    def perform_login(self):
        """
        Handles the login button click.
        """
        username = self.user_entry.get()
        password = self.pass_entry.get()

        if not username or not password:
            self.ui_manager.show_warning("Input Error", "请输入学号和密码")
            return

        self.ui_manager.update_status("正在登录...")
        self.ui_manager.disable_buttons()

        # Run login in a thread to avoid freezing the UI
        threading.Thread(target=self._login_thread, args=(username, password), daemon=True).start()

    def _login_thread(self, username, password):
        """
        Worker thread for logging in.
        """
        try:
            success, message = self.client.login(username, password)
            self.after(0, self._handle_login_result, success, message)
        except Exception as e:
            self.after(0, lambda: self.ui_manager.show_error("Login Error", str(e)))
            self.after(0, lambda: self.ui_manager.update_status(f"登录时发生错误: {e}"))
            self.after(0, lambda: self.ui_manager.enable_buttons(enable_login=True))

    def _handle_login_result(self, success, message):
        """
        处理登录结果
        """
        if success:
            welcome_msg = "登录成功！请点击获取活动列表。"
            self.ui_manager.update_status(welcome_msg)
            self.ui_manager.update_login_state(True)
        else:
            self.ui_manager.update_status(f"登录失败: {message}")
            self.ui_manager.show_error("Login Failed", message)
            self.ui_manager.enable_buttons(enable_login=True)

    def start_data_fetch(self):
        """
        Handles the "Fetch Activities" button click.
        """
        self.ui_manager.update_status("正在获取活动列表...")
        self.ui_manager.disable_buttons()
        self.ui_manager.clear_tree()
        self.activity_data_cache = []  # 清空缓存

        # 使用活动获取器线程
        self.fetcher_thread = ActivityFetcherThread(self.fetcher)
        self.fetcher_thread.start(
            on_complete=self._handle_fetch_all_complete,
            on_update=self._handle_fetch_update
        )

    def _handle_fetch_update(self, message):
        """
        处理数据获取过程中的更新消息
        """
        self.after(0, lambda: self.ui_manager.update_status(message))

    def _handle_fetch_all_complete(self, success, result, error):
        """
        处理所有活动数据获取完成
        """
        if success:
            self.activity_data_cache = result
            if not result:
                name_prefix = f"{self.student_name}同学，" if self.student_name else ""
                self.after(0, lambda: self.ui_manager.update_status(f"{name_prefix}未找到任何已报名的活动。"))
            else:
                # 更新学生姓名（因为活动列表页面可能包含更准确的姓名）
                new_name = self.client.get_student_name()
                if new_name and new_name != self.student_name:
                    self.student_name = new_name
                self.after(0, lambda: self.ui_manager.update_tree(self.activity_data_cache))
        else:
            self.after(0, lambda: self.ui_manager.show_error("Data Fetch Error", str(error)))
            self.after(0, lambda: self.ui_manager.update_status(f"获取数据失败: {error}"))

        self.after(0, lambda: self.ui_manager.enable_buttons())

    def fetch_detail_on_double_click(self, event):
        """
        Handles double-click event on the Treeview to fetch detail for a single activity.
        """
        # 1. 获取选中的行
        item_id = self.tree.focus()
        if not item_id:
            return

        # 2. 获取选中行的索引 (用于查找缓存数据)
        selected_index = self.tree.index(item_id)

        # 3. 检查缓存数据是否已加载
        if selected_index < 0 or selected_index >= len(self.activity_data_cache):
            return

        activity_info = self.activity_data_cache[selected_index]

        if activity_info.get('is_loaded'):
            return

        # 4. 未加载，开始按需获取
        self.ui_manager.update_status(f"正在获取 {activity_info['name']} 的详情...")
        self.ui_manager.disable_buttons()
        self.ui_manager.set_cursor("wait")

        # 使用活动获取器线程
        self.fetcher_thread = ActivityFetcherThread(self.fetcher)
        self.fetcher_thread.start(
            detail_url=activity_info['url'],
            index=selected_index,
            on_complete=self._handle_fetch_single_complete
        )

    def _handle_fetch_single_complete(self, success, result, error):
        """
        处理单个活动详情获取完成
        """
        if success:
            detail_data = result['detail']
            index = result['index']

            # 更新缓存
            self.activity_data_cache[index].update(detail_data)

            # 重新排序
            self.activity_data_cache.sort(
                key=lambda x: x.get('acttime_timestamp', 0),
                reverse=True
            )

            # 更新表格
            self.after(0, lambda: self.ui_manager.update_tree(self.activity_data_cache))
            name_prefix = f"{self.student_name}同学，" if self.student_name else ""
            self.after(0, lambda: self.ui_manager.update_status(
                f"{name_prefix}详情获取成功。"
            ))
        else:
            self.after(0, lambda: self.ui_manager.show_error("Fetch Detail Error", str(error)))
            self.after(0, lambda: self.ui_manager.update_status(f"获取详情失败: {error}"))

        self.after(0, lambda: self.ui_manager.enable_buttons())
        self.after(0, lambda: self.ui_manager.set_cursor(""))

if __name__ == "__main__":
    # Ensure you have the required libraries:
    # pip install requests beautifulsoup4 colorama
    app = ActivityViewer()
    app.mainloop()
