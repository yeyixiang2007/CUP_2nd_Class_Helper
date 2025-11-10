# ui_manager.py

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any

class UIManager:
    """
    UI管理器类，负责管理和更新应用程序的用户界面组件。
    """

    def __init__(self, root, tree):
        """
        初始化UI管理器。

        Args:
            root: 主窗口实例
            tree: Treeview表格实例
        """
        self.root = root
        self.tree = tree
        self._setup_tree_tags()

    def _setup_tree_tags(self):
        """
        设置Treeview的标签样式。
        定义不同活动状态对应的颜色标签。
        """
        # 定义三种行颜色标签
        self.tree.tag_configure("Completed", background="light green", foreground="black") # 已完成活动
        self.tree.tag_configure("Incomplete", background="#FFC0CB", foreground="black") # 未完成活动（浅粉色）
        self.tree.tag_configure("Unknown", foreground="gray") # 默认/未加载详情

    def update_status(self, message):
        """
        更新状态栏消息。

        Args:
            message: 要显示的状态消息
        """
        if hasattr(self.root, 'status_var'):
            self.root.status_var.set(message)

    def disable_buttons(self):
        """
        禁用相关按钮，防止用户在操作进行中重复点击。
        """
        if hasattr(self.root, 'fetch_button'):
            self.root.fetch_button.config(state="disabled")
        if hasattr(self.root, 'login_button'):
            self.root.login_button.config(state="disabled")

    def enable_buttons(self, enable_fetch=True, enable_login=False):
        """
        启用相关按钮。

        Args:
            enable_fetch: 是否启用获取按钮
            enable_login: 是否启用登录按钮
        """
        if enable_fetch and hasattr(self.root, 'fetch_button'):
            self.root.fetch_button.config(state="normal")
        if enable_login and hasattr(self.root, 'login_button'):
            self.root.login_button.config(state="normal")

    def update_tree(self, activity_data_cache: List[Dict[str, Any]]):
        """
        更新Treeview表格，根据完成状态应用颜色标签。

        Args:
            activity_data_cache: 活动数据列表
        """
        self.clear_tree()

        for item in activity_data_cache:
            # 1. 确定状态和标签
            tag = "Unknown" # 默认/未加载的活动

            # 仅对已加载详情的活动应用颜色
            if item.get('is_loaded', False):
                # 判断是否签到签退都已完成
                signin_ok = item.get('signin') == '已签到'
                signout_ok = item.get('signout') == '已签退'

                if signin_ok and signout_ok:
                    tag = "Completed" # 绿色 (已完成)
                else:
                    tag = "Incomplete" # 粉色 (未完成)

            # 2. 准备行数据
            row_values = (
                item['name'],
                item['time'],
                item['duration'],
                item['points'],
                item['signin'],
                item['signout'],
                item['tags']
            )

            # 3. 插入行，并应用标签
            self.tree.insert('', 'end', values=row_values, tags=(tag,))

        self.update_status(f"共找到 {len(activity_data_cache)} 条报名记录。")

    def clear_tree(self):
        """
        清空Treeview中的所有项
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

    def show_error(self, title, message):
        """
        显示错误消息框
        """
        messagebox.showerror(title, message)

    def show_warning(self, title, message):
        """
        显示警告消息框
        """
        messagebox.showwarning(title, message)

    def set_cursor(self, cursor_type=""):
        """
        设置光标类型
        """
        if hasattr(self.root, 'tree'):
            self.root.tree.config(cursor=cursor_type)

    def update_login_state(self, logged_in, username=None):
        """
        更新登录状态UI
        """
        if logged_in:
            if hasattr(self.root, 'fetch_button'):
                self.root.fetch_button.config(state="normal")
            if hasattr(self.root, 'user_entry'):
                self.root.user_entry.config(state="disabled")
            if hasattr(self.root, 'pass_entry'):
                self.root.pass_entry.config(state="disabled")
        else:
            if hasattr(self.root, 'login_button'):
                self.root.login_button.config(state="normal")
