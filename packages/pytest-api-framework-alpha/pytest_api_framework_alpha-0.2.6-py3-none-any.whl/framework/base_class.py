import traceback
import importlib
from datetime import datetime, timedelta
from urllib.parse import urlparse, urlunparse, urljoin

import pytest
from box import Box

from framework.exit_code import ExitCode
from framework.db.redis_db import RedisDB
from framework.db.mysql_db import MysqlDB
from framework.utils.log_util import logger
from framework.render_data import RenderData
from framework.http_client import ResponseUtil
from framework.settings import UNAUTHORIZED_CODE, FAKER_LANGUAGE
from framework.utils.common import snake_to_pascal, SingletonFaker
from framework.global_attribute import CONFIG, GlobalAttribute, _FRAMEWORK_CONTEXT
from framework.utils.mock_util import get_customized_kytmock, set_customized_kytmock, PaymentType, RiskLevel, IsDelayed

module = importlib.import_module("test_case.conftest")


class BaseTestCase(object):
    http = None
    data: Box = None
    scenario: Box = None
    belong_app = None
    response: ResponseUtil = None
    context: GlobalAttribute = None
    config: GlobalAttribute = None
    # faker方法文档 https://blog.csdn.net/m0_60052979/article/details/126368024
    faker = SingletonFaker(locale=FAKER_LANGUAGE).faker

    def request(self, app=None, *, account, data, **kwargs):
        try:
            app = self.default_app(app)
            app_http = getattr(self.http, app)
            domain = self.context.get(app).get("domain")
            data = RenderData(data).render()
            data.request.url = self.replace_domain(data.request.url, domain)
            self.response = getattr(app_http, account).request(data=data, kwargs=kwargs)
            if self.response.status_code in UNAUTHORIZED_CODE:
                _http = _FRAMEWORK_CONTEXT.get(key="_http")
                setattr(_http, app, getattr(module, f"{snake_to_pascal(app)}Login")(app))
                token_expiry = self.context_get("token_expiry")
                expire_time = datetime.now() + timedelta(seconds=token_expiry)
                _FRAMEWORK_CONTEXT.set(app=app, key="expire_time", value=expire_time)
            return self.response
        except AttributeError as e:
            logger.error(e)
            traceback.print_exc()
            pytest.exit(ExitCode.APP_OR_ACCOUNT_NOT_EXIST)
            return None

    def post(self, app, account, url, data=None, json=None, **kwargs):
        domain = self.context.get(app).get("domain")
        request = {"url": urljoin(domain, url), "data": data, "json": json}
        request.update({"method": "post", "headers": {}, **kwargs})
        return self.request(app=app, account=account, data=Box({"request": request}))

    def get(self, app, account, url, params=None, **kwargs):
        domain = self.context.get(app).get("domain")
        request = {"url": urljoin(domain, url), "params": params}
        request.update({"method": "get", "headers": {}, **kwargs})
        return self.request(app=app, account=account, data=Box({"request": request}))

    def put(self, app, account, url, data=None, json=None, **kwargs):
        domain = self.context.get(app).get("domain")
        request = {"url": urljoin(domain, url), "data": data, "json": json}
        request.update({"method": "put", "headers": {}, **kwargs})
        return self.request(app=app, account=account, data=Box({"request": request}))

    def delete(self, app, account, url, **kwargs):
        domain = self.context.get(app).get("domain")
        request = {"url": urljoin(domain, url)}
        request.update({"method": "delete", "headers": {}, **kwargs})
        return self.request(app=app, account=account, data=Box({"request": request}))

    def mysql_conn(self, db, app=None) -> MysqlDB:
        try:
            return _FRAMEWORK_CONTEXT.get(app=self.default_app(app), key="mysql").get(db)
        except AttributeError as e:
            traceback.print_exc()
            pytest.exit(ExitCode.LOAD_DATABASE_INFO_ERROR)

    def redis_conn(self, db, index=0, app=None) -> RedisDB:
        try:
            return _FRAMEWORK_CONTEXT.get(app=self.default_app(app), key="redis").get(db)[index]
        except AttributeError as e:
            traceback.print_exc()
            pytest.exit(ExitCode.LOAD_DATABASE_INFO_ERROR)

    def context_set(self, key, value):
        self.context.set(app=self.belong_app, key=key, value=value)

    def context_get(self, key):
        return self.context.get(app=self.belong_app, key=key)

    def default_app(self, app):
        return app or self.belong_app

    @staticmethod
    def replace_domain(url: str, new_base: str) -> str:
        """
        替换 URL 的 scheme 和 netloc（协议和域名）。
        :param url: 原始 URL
        :param new_base: 新的 base，如 'https://new.example.com'
        :return: 替换后的 URL
        """
        parsed_url = urlparse(url)
        new_base_parsed = urlparse(new_base)

        updated_url = parsed_url._replace(
            scheme=new_base_parsed.scheme,
            netloc=new_base_parsed.netloc
        )
        return urlunparse(updated_url)

    def get_customized_kytmock(self, request_id):
        return get_customized_kytmock(self.context.get("env"), request_id)

    def set_customized_kytmock(self, request_id, payment_type: PaymentType, risk_level: RiskLevel, is_delayed: IsDelayed = IsDelayed.NO_DELAY):
        """
          参数:
            env: 环境名称（如
            "dev", "test"）
            request_id: 请求ID
            payment_type: 支付类型枚举
            risk_level: 风险等级枚举
            is_delayed: 是否延迟枚举，默认不延迟
            custom_url: 自定义URL（可选，用于临时测试特殊地址）

            返回:
            接口响应的JSON字典，失败则返回None

        """
        return set_customized_kytmock(self.context.get("env"), request_id, payment_type, risk_level, is_delayed)
