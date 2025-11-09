# network_client.py

from colorama import Fore
from colorama import Style
import requests
import src.config as config
import src.html_parser as html_parser
from typing import Tuple, Dict, Any
from urllib.parse import urlparse, parse_qs

class ApiClient:
    # ... (init, login, get_activity_list methods remain the same)

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.BASE_HEADERS)
        self.logged_in = False
        self.student_name = None  # 保存学生姓名

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        print(f"{Fore.YELLOW}{Style.BRIGHT}正在登录: {username}")
        try:
            # Step 0: GET login page to get execution token
            login_page_resp = self.session.get(
                config.LOGIN_URL,
                params={'service': config.SERVICE_URL}
            )
            login_page_resp.raise_for_status()

            # Parse execution token from HTML
            execution = html_parser.parse_execution(login_page_resp.text)
            if not execution:
                return False, "Failed to find login token (execution)."

            # Step 1: POST login data
            payload = {
                'username': username,
                'password': password,
                'submit': 'LOGIN',
                'type': 'username_password',
                'execution': execution,
                '_eventId': 'submit'
            }

            # Step 2: POST login data
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
        if not self.logged_in:
            raise Exception("User is not logged in.")

        try:
            # Step 3: Access the activity list page
            resp = self.session.get(config.ACTIVITY_LIST_URL)
            resp.raise_for_status()

            html_content = resp.text
            name = html_parser.parse_student_name(html_content)
            if name:
                self.student_name = name
                print(f"{Fore.YELLOW}{Style.BRIGHT}登录学生姓名: {self.student_name}")

            return html_content
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch activity list: {e}")

    def get_student_name(self) -> str | None:
        """
        获取已保存的学生姓名
        """
        return self.student_name

    def get_activity_detail(self, detail_url: str) -> Dict[str, Any]:
        """
        Fetches the activity details directly from the API.
        """
        if not self.logged_in:
            raise Exception("User is not logged in.")

        try:
            # Extract id and actid from the detail_url
            parsed_url = urlparse(detail_url)
            query_params = parse_qs(parsed_url.query)

            # API requires 'id' (which is enterMember ID) and 'actid'
            payload = {
                'id': query_params.get('id', [''])[0],
                'actid': query_params.get('actid', [''])[0]
            }

            if not payload['id'] or not payload['actid']:
                raise ValueError(f"Could not extract 'id' and 'actid' from URL: {detail_url}")

            # Step 4: Access the detail API using POST
            # FIX: Use the corrected ACTIVITY_DETAIL_API (now /detail)
            resp = self.session.post(
                config.ACTIVITY_DETAIL_API,
                data=payload, # Send parameters as POST data
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            resp.raise_for_status() # This will catch the 404 error if it still exists

            json_response = resp.json()

            # The status '1' indicates success
            if json_response.get('status') == '1':
                return json_response.get('data', {}) # Return the 'data' payload for parser
            else:
                raise Exception(f"API returned error status: {json_response.get('message', 'Unknown error')}")

        except requests.RequestException as e:
            # The 'Failed to fetch activity detail via API: 404 Client Error: Not Found' error is caught here
            raise Exception(f"Failed to fetch activity detail via API: {e}")
        except Exception as e:
            raise e
