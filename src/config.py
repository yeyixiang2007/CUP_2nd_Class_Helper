# config.py

# URLs derived from the request analysis
LOGIN_URL = "https://sso.cup.edu.cn/login"
# The 'service' parameter for the login request
SERVICE_URL = "https://sct.cup.edu.cn/ucenter/index/saveticket"
# Base URL for prepending to relative links
BASE_URL = "https://sct.cup.edu.cn"
# URL for the activity list page (My Page)
ACTIVITY_LIST_URL = "https://sct.cup.edu.cn/mucenter/index/index"
# The API is the detail path itself, expecting a POST request.
ACTIVITY_DETAIL_API = BASE_URL + "/activitynew/mucenter/enter/detail"

# User-Agent string to mimic a mobile browser
USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1 Edg/142.0.0.0"

# Standard headers to use in the session
BASE_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image:apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
    'User-Agent': USER_AGENT
}

DETAIL_FETCH_LIMIT = 10
