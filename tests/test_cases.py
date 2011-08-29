from infi.unittest import TestCase
from forge import Forge

class ForgeTest(TestCase):
    def setUp(self):
        super(ForgeTest, self).setUp()
        self.forge = Forge()
    def tearDown(self):
        self.forge.verify()
        self.forge.restore_all_replacements()
        self.forge.reset()
        super(ForgeTest, self).tearDown()
