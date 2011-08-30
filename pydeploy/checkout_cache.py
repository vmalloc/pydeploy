import os
from hashlib import sha1
from . import os_api
from .python3_compat import make_bytes

_CHECKOUT_CACHE_NAME = ".checkout_cache"

class CheckoutCache(object):
    def __init__(self, root):
        super(CheckoutCache, self).__init__()
        self._path = os.path.join(root, _CHECKOUT_CACHE_NAME)
        if not os_api.directory_exists(self._path):
            os_api.makedirs(self._path)
    def get_checkout_path(self, url):
        return os.path.join(self._path, sha1(make_bytes(url)).hexdigest())
