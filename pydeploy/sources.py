from .scm.git import clone_to_or_update as git_clone_to_or_update

_all_exposed_sources = {}

def _exposed(thing):
    _all_exposed_sources[thing.__name__] = thing
    return thing

class Source(object):
    def checkout(self, env):
        raise NotImplementedError()
    def install(self, env):
        raise NotImplementedError()

@_exposed
class Git(Source):
    def __init__(self, url):
        super(Git, self).__init__()
        self._url = url
    def install(self, env):
        checkout_path = self.checkout(env)
        env.install(checkout_path)
    def checkout(self, env):
        path = env.checkout_cache.get_checkout_path(self._url)
        git_clone_to_or_update(self._url, path)
        return path

@_exposed
class Path(Source):
    def __init__(self, path):
        super(Path, self).__init__()
        self._path = path
    def install(self, env):
        env._run_local_python(["setup.py", "install"], cwd=self._path)

@_exposed
class PIP(Source):
    def __init__(self, name):
        super(PIP, self).__init__()
        self._name = name
    def install(self, env):
        env.execute_script_assert_success("pip", "install", self._name)

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
