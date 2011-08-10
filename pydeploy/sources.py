import os
import logging
from .scm import git

_all_exposed_sources = {}
_logger = logging.getLogger("pydeploy.sources")

def _exposed(thing):
    _all_exposed_sources[thing.__name__] = thing
    return thing

class Source(object):
    def checkout(self, env, path=None):
        raise NotImplementedError() # pragma: no cover
    def install(self, env):
        raise NotImplementedError() # pragma: no cover
    def get_signature(self):
        raise NotImplementedError() # pragma: no cover
    def get_name(self):
        raise NotImplementedError() # pragma: no cover
    @classmethod
    def from_anything(cls, source):
        if not isinstance(source, Source):
            if isinstance(source, basestring):
                source = cls.from_string(source)
            else:
                source = EasyInstall(source)
        return source
    @classmethod
    def from_string(cls, source):
        if os.path.exists(os.path.expanduser(source)):
            return Path(source)
        try:
            return SCM(source)
        except InvalidSCMURL:
            pass
        return EasyInstall(source)

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

class SCMSource(Source):
    _DEFAULT_BRANCH = None
    def __init__(self, url, branch=None):
        super(SCMSource, self).__init__()
        if branch is None:
            branch = self._DEFAULT_BRANCH
        self._url = url
        self._branch = branch
    def __repr__(self):
        return "{0}({1})".format(type(self).__name__, self.get_name())
    def get_name(self):
        return '{0}@{1}'.format(self._url, self._branch)
    def get_signature(self):
        return repr(self)
    @classmethod
    def from_string(cls, s):
        if '@' in s:
            repo_url, branch_name = s.split("@", 1)
        else:
            repo_url = s
            branch_name = None
        return cls(repo_url, branch_name)
    @classmethod
    def get_prefix(cls):
        raise NotImplementedError() # pragma: no cover

@_exposed
class Git(SCMSource):
    _DEFAULT_BRANCH = 'master'
    def install(self, env):
        checkout_path = self.checkout(env)
        Path(checkout_path).install(env)
    def checkout(self, env, path=None):
        if path is None:
            path = env.get_checkout_cache().get_checkout_path(self._url)
        git.clone_to_or_update(self._url, branch=self._branch, path=path)
        return path
    @classmethod
    def get_prefix(cls):
        return 'git://'

@_exposed
class Path(SignedSingleParam):
    def __init__(self, *args, **kwargs):
        super(Path, self).__init__(*args, **kwargs)
        self._param = os.path.expanduser(self._param)
    def install(self, env):
        self._run_pydeploy_setup(env)
        env.utils.execute_python_script(["setup.py", "install"], cwd=self._param)
    def _run_pydeploy_setup(self, env):
        pydeploy_setup_file = os.path.join(self._param, "pydeploy_setup.py")
        if os.path.exists(pydeploy_setup_file):
            env.execute_deployment_file(pydeploy_setup_file)
    def checkout(self, env, path=None):
        if path is not None:
            raise NotImplementedError()
        return self._param

@_exposed
class PIP(SignedSingleParam):
    def install(self, env):
        env.execute_pip_install(self._param)
@_exposed
class EasyInstall(SignedSingleParam):
    def install(self, env):
        env.execute_easy_install(self._param)

@_exposed
class URL(PIP):
    pass

class InvalidSCMURL(ValueError):
    pass

@_exposed
def SCM(source):
    for source_class in _KNOWN_SCMS:
        if source.startswith(source_class.get_prefix()):
            return source_class.from_string(source)
    raise InvalidSCMURL("Unsupported SCM source: {0!r}".format(source))

_KNOWN_SCMS = [Git]

def get_all_sources_dict():
    return _all_exposed_sources
