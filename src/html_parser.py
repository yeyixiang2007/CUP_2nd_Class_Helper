# html_parser.py

from bs4 import BeautifulSoup
import re
from typing import Dict, Any
from datetime import datetime

def parse_execution(html_content: str) -> str | None:
    """
    解析登录页面HTML，提取'execution'令牌。

    Args:
        html_content: 登录页面的HTML内容

    Returns:
        str: execution令牌值，如果未找到则返回None
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    execution_input = soup.find('input', {'name': 'execution'})
    if execution_input and 'value' in execution_input.attrs:
        return execution_input['value']
    return None

def parse_student_name(html_content: str) -> str | None:
    """
    从HTML内容中解析学生姓名。

    Args:
        html_content: 包含学生信息的HTML内容

    Returns:
        str: 学生姓名，如果未找到则返回None
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    name_div = soup.select_one('div.name')

    if name_div:
        name = name_div.text.strip()
        if name:
            return name


    regex = r'<div class="name">([^<]+)</div>'
    match = re.search(regex, html_content)
    if match:
        name_from_regex = match.group(1).strip()
        if name_from_regex:
            return name_from_regex

    return None

def parse_activity_list(html_content: str) -> list[dict]:
    """
    解析"我的页面"HTML，提取已报名活动列表。

    Args:
        html_content: 我的页面的HTML内容

    Returns:
        list[dict]: 活动列表，每个字典包含：
            - 'name': 活动名称
            - 'url': 活动详情页面的相对 URL (包含id和actid)
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    activities = []

    # Select links under "我的报名" that are for activities
    activity_links = soup.select('li.green_events a[href*="/activitynew/mucenter/enter/detail"]')

    for link in activity_links:
        name_div = link.find('div', class_='course_name')
        if name_div:
            name = name_div.text.strip()
            url = link['href'] # This URL contains id and actid needed for the API
            activities.append({'name': name, 'url': url})

    return activities

def parse_activity_detail(json_data: Dict[str, Any]) -> dict:
    """
    解析活动详情JSON数据，提取关键信息。
    输入的json_data是API响应中的'data'字段。

    返回的字典包含：
    - 'time': 活动时间 (格式化)
    - 'acttime_timestamp': 活动时间戳 (用于排序)
    - 'duration': 持续时间
    - 'points': 积分
    - 'tags': 标签
    - 'signin': 签到状态 (不带时间)
    - 'signout': 签退状态 (不带时间)
    """
    activity = json_data.get('Activity', {})
    member = json_data.get('enterMember', {})

    def format_timestamp(ts):
        """
        格式化时间戳为 'YYYY-MM-DD HH:MM' 格式。
        如果输入无效或为空，返回 'N/A'。
        """
        try:
            ts = int(ts)
            if ts > 0:
                # 返回时间戳，用于排序
                return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
        except (ValueError, TypeError):
            pass
        return 'N/A'

    acttime_ts = activity.get('acttime')
    time_str = format_timestamp(acttime_ts)
    acttime_timestamp = int(acttime_ts) if acttime_ts and str(acttime_ts).isdigit() else 0

    duration_str = f"{activity.get('expectedtime', 'N/A')} 小时"
    points_str = str(activity.get('isopennum', '0'))

    tags = [
        activity.get('classificationtitle', ''),
        activity.get('categorytitle', '')
    ]
    if activity.get('issubmitwork') == '1':
        tags.append('需报告')
    tags_str = ' | '.join([t.strip() for t in tags if t])

    signin_status = '未签到'
    signout_status = '未签退'

    if member.get('signin') == '1':
        signin_status = '已签到'
    if member.get('signout') == '1':
        signout_status = '已签退'

    return {
        'time': time_str,
        'acttime_timestamp': acttime_timestamp,
        'duration': duration_str,
        'points': points_str,
        'tags': tags_str,
        'signin': signin_status,
        'signout': signout_status
    }

# 增加一个基本信息解析函数，用于未获取详情的活动
def parse_basic_activity_info(activity_data: dict) -> dict:
    """
    从活动详情数据中提取基本信息。

    Args:
        activity_data: 活动详情数据字典

    Returns:
        dict: 包含活动基本信息的字典
    """
    return {
        'name': activity_data['name'],
        'time': '双击获取详情',
        'acttime_timestamp': 0,
        'duration': '双击获取详情',
        'points': '双击获取详情',
        'tags': '双击获取详情',
        'signin': '双击获取详情',
        'signout': '双击获取详情'
    }
