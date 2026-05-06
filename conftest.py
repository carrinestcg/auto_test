import requests
import logging
import urllib3
from login_config import config
import pytest

# Token login hits this path under LOGIN_URL (same host as the browser login page).
_LOGIN_API_PATH = "tac/api/login/password"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseClient:
    def __init__(self):
        self.token=self._login()
        
    def _login(self):
        login_endpoint = f"{config.LOGIN_URL.rstrip('/')}/{_LOGIN_API_PATH}"
        origin = config.LOGIN_URL.rstrip("/")
        referer = origin + "/" if not config.LOGIN_URL.endswith("/") else config.LOGIN_URL
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": "",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Merchant": config.MERCHANT_CODE,
            "MerchantCode": config.MERCHANT_CODE,
            "Origin": origin,
            "Referer": referer,
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
            ),
            "environment": "",
            "language": "zh_CN",
            "noErrorNotice": "true",
            "platform": "",
        }
        cookies = {"language": "zh_CN"}
        resp = requests.post(
            login_endpoint,
            json=config.CREDENTIALS,
            headers=headers,
            cookies=cookies,
            verify=False,
        )
        logging.info("Login status code: %s", resp.status_code)
        resp.raise_for_status()
        token_data = resp.json()
        token = token_data.get("token")
        if not token:
            logging.error("Login JSON missing token: %s", token_data)
            raise ValueError("Login response missing token")
        return token
    
    def _headers(self):
        # Align with promo achievement API curl:
        # accept, merchantCode, operatorName, Authorization, Content-Type
        return {
            "accept": "application/json",
            "merchantCode": config.MERCHANT_CODE,
            "operatorName": config.CREDENTIALS["operatorName"],
            "Authorization": self.token,
            "Content-Type": "application/json",
        }
        
        
@pytest.fixture(scope="session")
def client():
    return BaseClient()

@pytest.fixture(scope="session")
def admin_token(client):
    return client.token

@pytest.fixture(scope="session")
def api_session(client):
    session = requests.Session()
    session.headers.update(client._headers())
    session.cookies.update({"language": "zh_CN"})
    session.verify = False
    yield session
    session.close()

@pytest.fixture(scope="session")
def platform():
    return config.MERCHANT_CODE