# network_client.py

from colorama import Fore
from colorama import Style
import requests
import src.config as config
import src.html_parser as html_parser
from typing import Tuple, Dict, Any
from urllib.parse import urlparse, parse_qs

class ApiClient:
    """
    API客户端类，处理与第二课堂系统的网络交互。
    负责登录、获取活动列表和活动详情等功能。
    """

    def __init__(self):
        """
        初始化ApiClient实例。
        设置会话、请求头，并初始化登录状态。
        """
        self.session = requests.Session()
        self.session.headers.update(config.BASE_HEADERS)
        self.logged_in = False
        self.student_name = None  # 保存学生姓名

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        用户登录函数。

        Args:
            username: 用户名（学号）
            password: 密码

        Returns:
            Tuple[bool, str]: (登录是否成功, 消息)
        """
        print(f"{Fore.YELLOW}{Style.BRIGHT}正在登录: {username}")
        try:
            # 获取登录页面以获取execution令牌
            login_page_resp = self.session.get(
                config.LOGIN_URL,
                params={'service': config.SERVICE_URL}
            )
            login_page_resp.raise_for_status()

            # 从HTML中解析execution令牌
            execution = html_parser.parse_execution(login_page_resp.text)
            if not execution:
                return False, "未找到登录令牌(execution)。"

            # 提交登录表单
            payload = {
                'username': username,
                'password': password,
                'submit': 'LOGIN',
                'type': 'username_password',
                'execution': execution,
                '_eventId': 'submit'
            }

            login_resp = self.session.post(
                config.LOGIN_URL,
                params={'service': config.SERVICE_URL},
                data=payload,
                allow_redirects=False
            )

            if login_resp.status_code == 302 and 'Location' in login_resp.headers:
                ticket_url = login_resp.headers['Location']
                self.session.get(ticket_url)
                self.logged_in = True
                return True, "Login successful"
            else:
                return False, "Login failed. Check credentials."

        except requests.RequestException as e:
            return False, f"Network error during login: {e}"

    def get_activity_list(self) -> str:
        """
        获取活动列表页面HTML。

        Returns:
            str: 活动列表页面HTML内容

        Raises:
            Exception: 当用户未登录或请求失败时抛出
        """
        if not self.logged_in:
            raise Exception("用户未登录。")

        try:
            # 访问活动列表页面
            resp = self.session.get(config.ACTIVITY_LIST_URL)
            resp.raise_for_status()

            html_content = resp.text
            name = html_parser.parse_student_name(html_content)
            if name:
                self.student_name = name
                print(f"{Fore.YELLOW}{Style.BRIGHT}登录学生: {self.student_name}")

            return html_content
        except requests.RequestException as e:
            raise Exception(f"获取活动列表失败: {e}")

    def get_student_name(self) -> str | None:
        """
        获取学生姓名。

        Returns:
            str: 学生姓名，如果未获取则返回None
        """
        return self.student_name

    def get_activity_detail(self, detail_url: str) -> Dict[str, Any]:
        """
        获取单个活动的详细信息。

        Args:
            detail_url: 活动详情页面的URL

        Returns:
            Dict[str, Any]: 包含活动详情的字典

        Raises:
            Exception: 当用户未登录或请求失败时抛出
        """
        if not self.logged_in:
            raise Exception("用户未登录。")

        try:
            # 从detail_url中提取id和actid参数
            parsed_url = urlparse(detail_url)
            query_params = parse_qs(parsed_url.query)

            # API需要'id'（即enterMember ID）和'actid'
            payload = {
                'id': query_params.get('id', [''])[0],
                'actid': query_params.get('actid', [''])[0]
            }

            if not payload['id'] or not payload['actid']:
                raise ValueError(f"无法从URL中提取'id'和'actid': {detail_url}")

            # 访问详情API
            resp = self.session.post(
                config.ACTIVITY_DETAIL_API,
                data=payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            resp.raise_for_status()

            json_response = resp.json()

            # 状态码'1'表示成功
            if json_response.get('status') == '1':
                return json_response.get('data', {}) # 返回'data'部分供解析器使用
            else:
                raise Exception(f"API返回错误状态: {json_response.get('message', '未知错误')}")

        except requests.RequestException as e:
            # 这里捕获'Failed to fetch activity detail via API: 404 Client Error: Not Found'错误
            raise Exception(f"通过API获取活动详情失败: {e}")
        except Exception as e:
            raise e
