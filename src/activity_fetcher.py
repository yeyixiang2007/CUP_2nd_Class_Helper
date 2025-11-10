# activity_fetcher.py

import threading
import src.html_parser as html_parser
from typing import List, Dict, Any, Tuple
from colorama import Fore, Style

class ActivityFetcher:
    """
    活动数据获取器类，负责获取活动列表和活动详情。
    """
    
    def __init__(self, client, detail_fetch_limit=5):
        """
        初始化活动获取器。
        
        Args:
            client: API客户端实例
            detail_fetch_limit: 预加载详情的活动数量限制
        """
        self.client = client
        self.detail_fetch_limit = detail_fetch_limit

    def fetch_all_activities(self, callback=None) -> List[Dict[str, Any]]:
        """
        获取所有活动数据，并预先加载前N个活动的详情。
        
        Args:
            callback: 可选的进度回调函数
            
        Returns:
            List[Dict[str, Any]]: 包含活动数据的列表
        """
        activity_data_cache = []

        try:
            # 获取活动列表（包含名称和URL）
            list_html = self.client.get_activity_list()
            activities = html_parser.parse_activity_list(list_html)

            print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*80}")
            print(f"{Fore.CYAN}{Style.BRIGHT}{'活动列表检索结果':^80}")
            print(f"{Fore.CYAN}{Style.BRIGHT}{'='*80}")

            if not activities:
                print(f"{Fore.YELLOW}{Style.BRIGHT}未找到任何已报名的活动。")
                return []

            print(f"{Fore.GREEN}{Style.BRIGHT}✓ 找到了 {len(activities)} 个活动，正在获取前 {self.detail_fetch_limit} 条详情...")

            # 2. 获取详情（限制前N个项目）
            for i, activity in enumerate(activities):
                if i < self.detail_fetch_limit:
                    # 预先获取详情
                    if callback:
                        callback(f"正在获取详情: {i+1}/{self.detail_fetch_limit} - {activity['name'][:30]}...")

                    try:
                        detail_data = self.client.get_activity_detail(activity['url'])
                        details = html_parser.parse_activity_detail(detail_data)

                        # 组合活动名称和详情，并标记为已加载
                        activity_data_cache.append({
                            **activity,
                            **details,
                            'is_loaded': True
                        })
                        print(f"{Fore.GREEN}✓ 详情获取成功: {activity['name']}")
                    except Exception as e:
                        error_msg = f"Error fetching detail for {activity['name']}: {e}"
                        print(f"{Fore.RED}✗ {error_msg}")
                        # 获取失败的也只显示基础信息
                        activity_data_cache.append({
                            **activity,
                            **html_parser.parse_basic_activity_info(activity),
                            'is_loaded': False
                        })
                else:
                    # 仅显示基础信息（超过限制的）
                    activity_data_cache.append({
                        **activity,
                        **html_parser.parse_basic_activity_info(activity),
                        'is_loaded': False
                    })

            # 3. 排序所有数据（按活动时间戳排序，降序排列最新的在前）
            activity_data_cache.sort(
                key=lambda x: x.get('acttime_timestamp', 0),
                reverse=True
            )

            return activity_data_cache

        except Exception as e:
            error_msg = f"获取数据失败: {e}"
            print(f"{Fore.RED}{Style.BRIGHT}✗ {error_msg}")
            raise

    def fetch_single_activity_detail(self, detail_url: str) -> Dict[str, Any]:
        """
        获取单个活动的详细信息。
        
        Args:
            detail_url: 活动详情页面的URL
            
        Returns:
            Dict[str, Any]: 活动详情数据
        """
        try:
            # 获取活动详情数据
            detail_data = self.client.get_activity_detail(detail_url)
            
            # 解析详情数据
            details = html_parser.parse_activity_detail(detail_data)
            
            # 返回带有加载标记的详情
            return {
                **details,
                'is_loaded': True
            }
        except Exception as e:
            print(f"{Fore.RED}获取活动详情失败: {str(e)}")
            # 返回基本信息和错误标记
            basic_info = html_parser.parse_basic_activity_info({'detail_url': detail_url})
            return {
                **basic_info,
                'is_loaded': True,
                'error': str(e)
            }

class ActivityFetcherThread:
    """
    活动获取线程类，用于在后台线程中执行活动数据获取操作。
    """
    
    def __init__(self, fetcher):
        """
        初始化活动获取线程。
        
        Args:
            fetcher: ActivityFetcher实例
        """
        self.fetcher = fetcher
        self.thread = None
        self.result = None
        self.error = None

    def start(self, detail_url=None, index=None, on_complete=None, on_update=None):
        """
        启动获取线程。
        
        Args:
            detail_url: 单个活动详情获取的可选URL
            index: 行索引（用于单个活动获取）
            on_complete: 获取完成时的可选回调函数
            on_update: 获取进度更新的可选回调函数
        """
        if detail_url is not None and index is not None:
            # 获取单个活动详情
            self.thread = threading.Thread(
                target=self._fetch_single_thread,
                args=(detail_url, index, on_complete, on_update),
                daemon=True
            )
        else:
            # 获取所有活动
            self.thread = threading.Thread(
                target=self._fetch_all_thread,
                args=(on_complete, on_update),
                daemon=True
            )
        self.thread.start()

    def _fetch_all_thread(self, on_complete=None, on_update=None):
        """
        获取所有活动的线程函数。
        
        Args:
            on_complete: 获取完成时的回调函数
            on_update: 获取进度更新的回调函数
        """
        try:
            self.result = self.fetcher.fetch_all_activities(callback=on_update)
            if on_complete:
                on_complete(True, self.result, None)
        except Exception as e:
            self.error = e
            if on_complete:
                on_complete(False, None, e)

    def _fetch_single_thread(self, detail_url, index, on_complete=None, on_update=None):
        """
        获取单个活动详情的线程函数。
        
        Args:
            detail_url: 活动详情URL
            index: 活动索引
            on_complete: 获取完成时的回调函数
            on_update: 获取进度更新的回调函数
        """
        try:
            self.result = self.fetcher.fetch_single_activity_detail(detail_url)
            if on_complete:
                on_complete(True, {'detail': self.result, 'index': index}, None)
        except Exception as e:
            self.error = e
            if on_complete:
                on_complete(False, None, e)

    def is_alive(self):
        """
        检查线程是否存活。
        
        Returns:
            bool: 线程是否正在运行
        """
        return self.thread.is_alive() if self.thread else False
