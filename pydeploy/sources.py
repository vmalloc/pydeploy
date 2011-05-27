import logging
from .scm.git import clone_to_or_update as git_clone_to_or_update

_all_exposed_sources = {}
_logger = logging.getLogger("pydeploy.sources")

def _exposed(thing):
    _all_exposed_sources[thing.__name__] = thing
    return thing

class Source(object):
    def checkout(self, env):
        raise NotImplementedError()
    def install(self, env):
        raise NotImplementedError()
    def get_signature(self):
        raise NotImplementedError()
    def get_name(self):
        raise NotImplementedError()

class SignedSingleParam(Source):
    def __init__(self, param):
        super(SignedSingleParam, self).__init__()
        self._param = param
    def get_signature(self):
        return repr(self)
    def get_name(self):
        return self._param
    def __repr__(self):
        return "{0}({1})".format(type(self).__name__, self._param)

@_exposed
class Git(SignedSingleParam):
    def install(self, env):
        checkout_path = self.checkout(env)
        Path(checkout_path).install(env)
    def checkout(self, env):
        path = env.checkout_cache.get_checkout_path(self._param)
        git_clone_to_or_update(self._param, path)
        return path

@_exposed
class Path(SignedSingleParam):
    def install(self, env):
        env._run_local_python(["setup.py", "install"], cwd=self._param)

@_exposed
class PIP(SignedSingleParam):
    def install(self, env):
        env.execute_script_assert_success("pip", "install", self._param)
@_exposed
class EasyInstall(SignedSingleParam):
    def install(self, env):
        env.execute_script_assert_success("easy_install", self._param)

@_exposed
class URL(PIP):
    pass

@_exposed
def SCM(url):
    if url.startswith("git://"):
        return Git(url)
    raise ValueError("Unsupported SCM source: {0!r}".format(url))

def get_all_sources_dict():
    return _all_exposed_sources
