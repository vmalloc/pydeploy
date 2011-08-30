import os
import tempfile
from .test_cases import ForgeTest
from pydeploy import os_api
from pydeploy.checkout_cache import CheckoutCache
from pydeploy.checkout_cache import _CHECKOUT_CACHE_NAME

class CheckoutCacheTest(ForgeTest):
    def setUp(self):
        super(CheckoutCacheTest, self).setUp()
        self.root = tempfile.gettempdir()
        self.expecetd_checkout_path = os.path.join(self.root, _CHECKOUT_CACHE_NAME)
        self.forge.replace_many(os_api, "makedirs", "directory_exists")
    def test__creates_if_not_exists(self):
        os_api.directory_exists(self.expecetd_checkout_path).and_return(False)
        os_api.makedirs(self.expecetd_checkout_path)
        self.forge.replay()
        c = CheckoutCache(self.root)
    def test__dont_create_if_not_exists(self):
        os_api.directory_exists(self.expecetd_checkout_path).and_return(True)
        self.forge.replay()
        c = CheckoutCache(self.root)
    def test__get_checkout_path(self):
        os_api.directory_exists(self.expecetd_checkout_path).and_return(True)
        self.forge.replay()
        c = CheckoutCache(self.root)
        url = "some.url"
        path1 = c.get_checkout_path(url)
        path2 = c.get_checkout_path(url)
        self.assertEquals(path1, path2)
        self.assertEquals(os.path.split(path1)[0], self.expecetd_checkout_path)
