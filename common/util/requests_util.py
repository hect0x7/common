from .typing_util import *
from .json_util import LazyDictModel


class Resp:

    @classmethod
    def wrap(cls, resp):
        if isinstance(resp, Resp):
            return resp
        return Resp(resp)

    def __init__(self, resp) -> None:
        self.resp: Response = resp
        self._cache_to_json: Optional[Dict] = None
        self._cache_to_model: Optional[LazyDictModel] = None

    def require_success(self):
        if self.is_not_success:
            raise NotImplementedError

    @property
    def is_success(self) -> bool:
        if self.resp.status_code != 200:
            return False

        return self.json()['code'] == 0

    @property
    def is_not_success(self) -> bool:
        return not self.is_success

    @property
    def text(self):
        return self.resp.text

    @property
    def res_data(self) -> dict:
        self.require_success()
        return self.json()['data']

    @property
    def model_data(self) -> LazyDictModel:
        self.require_success()
        return self.model().data

    def json(self, **kwargs) -> Dict:
        if self._cache_to_json is None:
            self._cache_to_json = self.resp.json(**kwargs)
        return self._cache_to_json

    def model(self) -> LazyDictModel:
        if self._cache_to_model is None:
            self._cache_to_model = LazyDictModel(self.json())
        return self._cache_to_model


class ProxyBuilder:
    proxy_protocols = ['https', 'http']
    addr_f = 'http://{}:{}'

    @classmethod
    def build_proxy(cls, address):
        proxies = {protocol: address for protocol in cls.proxy_protocols}
        return proxies

    @classmethod
    def clash_proxy(cls, ip='127.0.0.1', port='7890'):
        return cls.build_proxy(cls.addr_f.format(ip, port))

    @classmethod
    def v2Ray_proxy(cls, ip='127.0.0.1', port='10809'):
        return cls.build_proxy(cls.addr_f.format(ip, port))


def save_resp_content(resp: Response, filepath: str):
    from .file_util import of_dir_path
    of_dir_path(filepath, mkdir=True)
    with open(filepath, 'wb') as f:
        f.write(resp.content)


def set_global_proxy(status='off'):
    """
    全局性的关闭或者启用系统代理。
    测试时发现，如果设置了系统代理，在访问 https 网站时发生错误 requests.exceptions.ProxyError
    原因是 SSL: self._sslobj.do_handshake() -> OSError: [Errno 0] Error
    进一步，是因为 urllib3 1.26.0 以上版本支持 https协议，但是代理软件不支持，导致连接错误。
    所以使用 { 'https': 'http://127.0.0.1:1080' }，http的协议访问 https 的网址（本地通信），即可解决。
    或者在 requests.get 函数中增加 proxies={'https': None} 参数来解决，但每次访问都需加这个参数，太麻烦，
    此处通过修改 requests 库中的 get_environ_proxies 函数的方法来全局性地关闭系统代理，或者仅关闭 https 的代理。

    注意：仅影响本 Python程序的 requests包，不影响其他 Python程序，
    不影响 Windows系统的代理设置，也不影响浏览器的代理设置。

    :param status: status - 'off', 关闭系统代理；'on', 打开系统代理；'toggle', 切换关闭或者打开状态；
    """
    from requests import sessions, utils
    init_func = sessions.get_environ_proxies
    if status == 'off':
        # 关闭系统代理
        if init_func.__name__ == '<lambda>':
            # 已经替换了原始函数，即已经是关闭状态，无需设置
            return
        # 修改函数，也可以是 lambda *x, **y: {'https': None}
        sessions.get_environ_proxies = lambda *x, **y: {}
    elif status == 'on':
        # 打开系统代理，如果设置了代理的话
        # 对高版本的 urllib3(>1.26.0) 打补丁，修正 https代理 BUG: OSError: [Errno 0] Error
        # noinspection PyUnresolvedReferences
        proxies = utils.getproxies()
        if 'https' in proxies:
            proxies['https'] = proxies.get('http')  # None 或者 'http://127.0.0.1:1080'
        sessions.get_environ_proxies = lambda *x, **y: proxies
        sessions.get_environ_proxies.__name__ = 'get_environ_proxies'
    else:
        # 切换开关状态
        if init_func.__name__ == '<lambda>':
            # 已经是关闭状态
            set_global_proxy('on')
        else:
            # 已经是打开状态
            set_global_proxy('off')


def print_resp_json(resp: Response, indent=2):
    from .json_util import json_dumps
    json_str = json_dumps(resp.json(), indent=indent)
    from .sys_util import parse_unicode_escape_text
    print(parse_unicode_escape_text(json_str))


def WebKit_format(data, boundary="----WebKitFormBoundary*********ABC", headers=None):
    # 从headers中提取boundary信息
    if headers is None:
        headers = {}
    if "content-type" in headers:
        fd_val = str(headers["content-type"])
        if "boundary" in fd_val:
            fd_val = fd_val.split(";")[1].strip()
            boundary = fd_val.split("=")[1].strip()
        else:
            raise Exception("multipart/form-data头信息错误，请检查content-type key是否包含boundary")
    # form-data格式定式
    jion_str = '--{}\r\nContent-Disposition: form-data; name="{}"\r\n\r\n{}\r\n'
    end_str = "--{}--".format(boundary)
    args_str = ""
    if not isinstance(data, dict):
        raise Exception("multipart/form-data参数错误，data参数应为dict类型")
    for key, value in data.items():
        args_str += jion_str.format(boundary, key, value)
    args_str += end_str.format(boundary)
    args_str = args_str.replace("\'", "\"")
    return args_str
