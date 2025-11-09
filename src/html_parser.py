# html_parser.py

from bs4 import BeautifulSoup
import re
from typing import Dict, Any
from datetime import datetime

def parse_execution(html_content: str) -> str | None:
    """
    Parses the login page HTML to find the 'execution' token.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    execution_input = soup.find('input', {'name': 'execution'})
    if execution_input and 'value' in execution_input.attrs:
        return execution_input['value']
    return None

def parse_student_name(html_content: str) -> str | None:
    """
    Parses the student name from the HTML content.
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
    Parses the "My Page" HTML to find the list of registered activities.

    返回的每个字典包含：
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
    Parses the activity detail JSON data to extract key information.
    The input json_data is the 'data' field from the API response.

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

    # Helper to convert Unix timestamp string/int to YYYY-MM-DD HH:MM
    def format_timestamp(ts):
        try:
            ts = int(ts)
            if ts > 0:
                # 返回时间戳，用于排序
                return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
        except (ValueError, TypeError):
            pass
        return 'N/A'

    # Extract Activity Time
    acttime_ts = activity.get('acttime')
    time_str = format_timestamp(acttime_ts)
    # MODIFICATION: Save the timestamp for sorting. Use 0 if N/A.
    acttime_timestamp = int(acttime_ts) if acttime_ts and str(acttime_ts).isdigit() else 0

    # Extract Duration
    duration_str = f"{activity.get('expectedtime', 'N/A')} 小时"

    # Extract Points
    points_str = str(activity.get('isopennum', '0'))

    # Extract Tags
    tags = [
        activity.get('classificationtitle', ''),
        activity.get('categorytitle', '')
    ]
    # Check if report is required (issubmitwork: "1")
    if activity.get('issubmitwork') == '1':
        tags.append('需报告')

    # Filter out empty strings and join with a pipe for clarity
    tags_str = ' | '.join([t.strip() for t in tags if t])

    # Extract Sign-in/Sign-out status (MODIFICATION: No time displayed)
    signin_status = '未签到'
    signout_status = '未签退'

    if member.get('signin') == '1':
        signin_status = '已签到'

    if member.get('signout') == '1':
        signout_status = '已签退'

    return {
        'time': time_str,
        'acttime_timestamp': acttime_timestamp, # 新增字段用于排序
        'duration': duration_str,
        'points': points_str,
        'tags': tags_str,
        'signin': signin_status,
        'signout': signout_status
    }

# 增加一个基本信息解析函数，用于未获取详情的活动
def parse_basic_activity_info(activity_data: dict) -> dict:
    """
    Return basic info for activities that haven't fetched full details.
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
