import os
from hashlib import sha1

class CheckoutCache(object):
    def __init__(self, root):
        super(CheckoutCache, self).__init__()
        self._path = os.path.join(root, ".checkout_cache")
        if not os.path.exists(self._path):
            os.makedirs(self._path)
    def get_checkout_path(self, url):
        return os.path.join(self._path, sha1(url).hexdigest())
