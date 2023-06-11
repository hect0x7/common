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
        # import tls_client.response
        # Session = tls_client.Session
        # TlsResp = tls_client.response.Response
        # return self.Session('chrome_109')
        raise NotImplementedError('已移除对 tls_client 的支持')

    def fix_meta_data(self, meta_data):
        for k, v in self.tls_client_rename_kwargs.items():
            if k in meta_data:
                meta_data[v] = meta_data.pop(k)
        return meta_data


class CffiPostman(AbstractPostman):

    def __init__(self, kwargs) -> None:
        super().__init__(kwargs)

    def __get__(self):
        from curl_cffi import requests
        return requests.get

    def __post__(self):
        from curl_cffi import requests
        return requests.post


class CffiSessionPostman(AbstractSessionPostman):

    def create_session(self, kwargs):
        return self.new_cffi_session(kwargs)

    # noinspection PyMethodMayBeStatic
    def new_cffi_session(self, kwargs: dict):
        from curl_cffi import requests
        return requests.Session(**kwargs)

    def before_request(self, kwargs):
        return kwargs


# help typing
PostmanImplClazz = Union[
    Type[CffiPostman],
    Type[CffiSessionPostman],
    Type[RequestsPostman],
    Type[RequestsSessionPostman],
    Type[TslClientSessionPostman],
]


class Postmans:
    postman_impl_class_dict: Dict[str, PostmanImplClazz] = {
        'requests': RequestsPostman,
        'requests_Session': RequestsSessionPostman,
        'cffi': CffiPostman,
        'cffi_Session': CffiSessionPostman,
    }

    @classmethod
    def get_impl_clazz(cls, key='requests') -> PostmanImplClazz:
        return cls.postman_impl_class_dict[key]

    @classmethod
    def create(cls,
               filepath='./postman.yml',
               data=None,
               ) -> Postman:
        if data is None:
            from common import PackerUtil
            data = PackerUtil.unpack(filepath)[0]
            if data is None:
                raise AssertionError(f'空配置文件: {filepath}')

        return cls.PostmanDslBuilder().build_postman(data)

    # noinspection PyMethodMayBeStatic
    class PostmanDslBuilder:

        def __init__(self) -> None:
            self.dsl_handler_list: list[Callable[[Dict], Union[Postman, None]]] = [
                self.proxy_handler,
                self.impltype_handler,
            ]

        def proxy_handler(self, data: dict, key='proxies'):
            meta_data = data.get('meta_data', {})

            from common import ProxyBuilder

            proxies = meta_data.get(key, None)

            # 无代理，或代理已配置好好的
            if proxies is None or isinstance(proxies, dict):
                return

            meta_data[key] = ProxyBuilder.build_by_str(proxies)

        def impltype_handler(self, data: dict, key='type'):
            impl_clazz = Postmans.get_impl_clazz(data.get(key, 'requests'))
            return impl_clazz(data.get('meta_data', {}))

        def build_postman(self, data):
            for handler in self.dsl_handler_list:
                postman = handler(data)
                if postman is not None:
                    return postman

            raise NotImplementedError
