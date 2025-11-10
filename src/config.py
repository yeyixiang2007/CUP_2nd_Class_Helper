# config.py

# 登录页面URL
LOGIN_URL = "https://sso.cup.edu.cn/login"
# 登录请求中的'service'参数
SERVICE_URL = "https://sct.cup.edu.cn/ucenter/index/saveticket"
# 用于拼接相对链接的基础URL
BASE_URL = "https://sct.cup.edu.cn"
# 活动列表页面URL（我的页面）
ACTIVITY_LIST_URL = "https://sct.cup.edu.cn/mucenter/index/index"
# 活动详情API，需要POST请求
ACTIVITY_DETAIL_API = BASE_URL + "/activitynew/mucenter/enter/detail"

# 模拟移动浏览器的User-Agent字符串
USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1 Edg/142.0.0.0"

# 会话中使用的标准请求头
BASE_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image:apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
    'User-Agent': USER_AGENT
}

# 单次请求获取活动详情的限制数量
DETAIL_FETCH_LIMIT = 10
