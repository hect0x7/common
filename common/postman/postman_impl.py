from typing import Type, Dict, Union

from .postman_api import *


class RequestsPostman(AbstractPostman):

    def __get__(self):
        from requests import get
        return get

    def __post__(self):
        from requests import post
        return post


class RequestsSessionPostman(AbstractSessionPostman):

    def create_session(self, kwargs):
        import requests
        session = requests.Session()
        if 'cookies' in kwargs:
            session.cookies = requests.sessions.cookiejar_from_dict(kwargs.pop('cookies'))
        return session


class TslClientSessionPostman(AbstractSessionPostman):
    import tls_client.response
    Session = tls_client.Session
    TlsResp = tls_client.response.Response

    tls_client_rename_kwargs = {
        'proxies': 'proxy',
        'timeout': 'timeout_seconds'
    }

    def __init__(self, kwargs: dict) -> None:
        super().__init__(self.fix_meta_data(kwargs))

    def create_session(self, kwargs):
        return self.new_tls_client_Session()

    def before_request(self, kwargs):
        kwargs = self.fix_meta_data(kwargs)
        return super().before_request(kwargs)

    def new_tls_client_Session(self):
        return self.Session('chrome_109')

    def fix_meta_data(self, meta_data):
        for k, v in self.tls_client_rename_kwargs.items():
            if k in meta_data:
                meta_data[v] = meta_data.pop(k)
        return meta_data


class CffiPostman(AbstractPostman):

    def __init__(self, kwargs) -> None:
        kwargs.setdefault('impersonate', 'chrome101')
        super().__init__(kwargs)

    def __get__(self):
        from curl_cffi import requests
        return requests.get

    def __post__(self):
        from curl_cffi import requests
        return requests.post


class CffiSessionPostman(AbstractSessionPostman):
    from curl_cffi import requests
    Session = requests.Session
    CffiResp = requests.Response

    def __init__(self, kwargs: dict) -> None:
        kwargs.setdefault('impersonate', 'chrome101')
        super().__init__(kwargs)

    def create_session(self, kwargs):
        return self.new_cffi_session(kwargs)

    def new_cffi_session(self, kwargs: dict):
        return self.Session(**kwargs)


# help for typing
TlsResp = TslClientSessionPostman.TlsResp
CffiResp = CffiSessionPostman.CffiResp
PostmanImplClazz = Union[
    Type[CffiPostman],
    Type[CffiSessionPostman],
    Type[RequestsPostman],
    Type[RequestsSessionPostman],
    Type[TslClientSessionPostman],
]


class Postmans:
    postman_impl_class_dict: Dict[str, PostmanImplClazz] = {
        # 使用 requests，最基础的请求方式
        'requests': RequestsPostman,
        # 使用 requests.Session，自动维护 cookies
        'requests_Session': RequestsSessionPostman,
        # 使用以下支持伪装【tls指纹】的库，更加安全稳如苟
        'cffi': CffiPostman,
        'cffi_Session': CffiSessionPostman,
        # 注意: tls_client 不支持 response.content 和 cookies维护
        'tls_client': TslClientSessionPostman,
    }

    @classmethod
    def get_impl_clazz(cls, key: str) -> PostmanImplClazz:
        return cls.postman_impl_class_dict[key]
