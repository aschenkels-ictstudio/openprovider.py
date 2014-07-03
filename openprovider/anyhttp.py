# coding=utf-8


class HttpClient(object):
    """Superclass for all the HTTP client adapter implementations."""

    url = None
    headers = {"User-Agent": "openprovider.py/0.1"}

    def __init__(self, url):
        self.url = url

    def post(self, data):
        """Post some data to the Openprovider API."""
        raise NotImplementedError()

    @staticmethod
    def any(*args, **kwargs):
        try:
            return RequestsHttpClient(*args, **kwargs)
        except ImportError:
            return UrllibHttpClient(*args, **kwargs)


class RequestsHttpClient(HttpClient):
    """
    HttpClient implementation based on the Requests library. Does connection
    pooling, keep-alive and SSL verification. Preferred.
    """
    session = None

    def __init__(self, url):
        super(RequestsHttpClient, self).__init__(url)

        import requests

        self.session = requests.Session()
        self.session.verify = True
        self.session.headers.update(self.headers)

    def post(self, data):
        return self.session.post(self.url, data=data).content


class UrllibHttpClient(HttpClient):
    """
    HttpClient based on the built-in urllib (or urllib2) module. Does not do
    SSL verification. Fallback.
    """
    def __init__(self, url):
        super(UrllibHttpClient, self).__init__(url)

        try:
            import urllib.request as urllib
        except ImportError:
            import urllib2 as urllib

        self.urllib = urllib

    def post(self, data):
        req = self.urllib.Request(self.url, data, self.headers)
        response = self.urllib.urlopen(req)
        return response.read()