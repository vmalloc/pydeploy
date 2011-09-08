import os
import logging
from .scm import git
from . import exceptions
from .python3_compat import basestring
from pkg_resources import parse_version

_all_exposed_sources = {}
_logger = logging.getLogger("pydeploy.sources")

def _exposed(thing):
    _all_exposed_sources[thing.__name__] = thing
    return thing

class Source(object):
    def checkout(self, env, path=None):
        raise NotImplementedError() # pragma: no cover
    def install(self, env, reinstall):
        raise NotImplementedError() # pragma: no cover
    def get_signature(self):
        raise NotImplementedError() # pragma: no cover
    def get_name(self):
        raise NotImplementedError() # pragma: no cover
    def resolve_constraints(self, constraints):
        raise NotImplementedError() # pragma: no cover
    @classmethod
    def from_anything(cls, source):
        if not isinstance(source, Source):
            if not isinstance(source, basestring):
                raise ValueError(source)
            return cls.from_string(source)
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
    def install(self, env, reinstall):
        checkout_path = self.checkout(env)
        Path(checkout_path, name=self._url).install(env, reinstall)
    def checkout(self, env, path=None):
        if path is None:
            path = env.get_checkout_cache().get_checkout_path(self._url)
        git.clone_to_or_update(self._url, branch=self._branch, path=path)
        git.reset_submodules(path=path)
        return path
    @classmethod
    def get_prefix(cls):
        return 'git://'
    def resolve_constraints(self, constraints):
        if len(constraints) > 1:
            raise NotImplementedError() # pragma: no cover
        [(constraint_type, version)] = constraints
        remote_refs = git.get_remote_references_dict(self._url)
        if constraint_type == '==':
            ref = self._get_version_ref(remote_refs, version)
        elif constraint_type in (">=", ">"):
            ref = self._get_version_ref_from_minimal(remote_refs, version, inclusive = (constraint_type == '>='))
        else:
            raise NotImplementedError() # pragma: no cover
        if ref is None:
            raise exceptions.RequiredVersionNotFound("Could not find version {0}".format(version))
        _logger.info("Found match for %s%s on %s: %s", constraint_type, version, self._url, ref)
        return Git(self._url, branch=ref)
    def _get_version_ref(self, remote_refs, version):
        version = self._normalize_version(version)
        for remote_ref, normalized in self._iter_normalized_versions(remote_refs):
            if normalized == version:
                return remote_ref.to_ref_name()
        return None
    def _get_version_ref_from_minimal(self, remote_refs, version, inclusive):
        version = self._normalize_version(version)
        for remote_ref, normalized in self._iter_normalized_versions(remote_refs):
            if inclusive:
                matches = normalized >= version
            else:
                matches = normalized > version
            if matches:
                return remote_ref.to_ref_name()
        if git.Branch('master') in remote_refs:
            return git.Branch('master')
        return None
    def _iter_normalized_versions(self, collection):
        for ref_name in collection:
            normalized = self._normalize_version(ref_name)
            if normalized is None:
                continue
            yield ref_name, normalized
    def _normalize_version(self, version):
        if version.startswith("v") or version.startswith("V"):
            version = version[1:]
        return parse_version(version)

@_exposed
class Path(SignedSingleParam):
    def __init__(self, path, name=None):
        super(Path, self).__init__(path)
        self._param = os.path.expanduser(self._param)
        self._name = name if name is not None else self._param
    def install(self, env, reinstall):
        env.installer.install_unpacked_package(self._param, name=self._name, reinstall=reinstall)
    def checkout(self, env, path=None):
        if path is not None:
            raise NotImplementedError()
        return self._param

@_exposed
class PIP(SignedSingleParam):
    def install(self, env, reinstall):
        env.execute_pip_install(self._param, reinstall=reinstall)
@_exposed
class EasyInstall(SignedSingleParam):
    def install(self, env, reinstall):
        env.execute_easy_install(self._param, reinstall=reinstall)

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
