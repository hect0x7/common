from .postman_api import *


class PostmanProxy(Postman):

    def __init__(self, postman: Postman):
        self.postman = postman

    def get(self, *args, **kwargs):
        return self.postman.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.postman.post(*args, **kwargs)

    def get_meta_data(self, key=None, dv=None) -> dict:
        return self.postman.get_meta_data(key, dv)

    def copy(self):
        return self.__class__(self.postman.copy())


class FixUrlPostman(PostmanProxy):

    def __init__(self,
                 postman: Postman,
                 fix_url: str,
                 ):
        super().__init__(postman)
        self.fix_url = fix_url

    def get(self, url=None, **kwargs):
        return super().get(url or self.fix_url, **kwargs)

    def post(self, url=None, **kwargs):
        return super().post(url or self.fix_url, **kwargs)

    def copy(self):
        return self.__class__(self.postman.copy(), self.fix_url)


class RetryPostman(PostmanProxy):

    def __init__(self,
                 postman: Postman,
                 retry_times: int,
                 ):
        super().__init__(postman)
        self.retry_times = retry_times

    def retry_request(self, request, url, **kwargs):
        for _ in range(self.retry_times):
            try:
                return request(url, **kwargs)
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                self.excp_handle(e)

        return self.fallback(url, kwargs)

    def get(self, *args, **kwargs):
        return self.retry_request(super().get, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.retry_request(super().post, *args, **kwargs)

    def fallback(self, url, kwargs):
        pass

    def excp_handle(self, e):
        pass


class MultiPartPostman(PostmanProxy):

    def build_headers(self, data, kwargs):
        headers = kwargs.get('headers', None)
        if headers is None:
            headers = self.get_meta_data().get('headers', {})
        headers['Content-Type'] = data.content_type
        return headers

    def post(self, *args, **kwargs):
        data = kwargs.get('data', None)
        from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
        if isinstance(data, (MultipartEncoder, MultipartEncoderMonitor)):
            kwargs['headers'] = self.build_headers(data, kwargs)
        return super().post(*args, **kwargs)
