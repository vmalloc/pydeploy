from hashlib import sha512
from .python3_compat import urlparse, make_bytes, basestring
import ast
import distutils.sysconfig
import pickle
import os
import sys
import logging
import pkg_resources
import site
import subprocess
from contextlib import contextmanager
from . import command
from . import os_api
from . import virtualenv_api
from .environment_utils import EnvironmentUtils
from .installer import Installer
from .checkout_cache import CheckoutCache
from .sources import (
    get_all_sources_dict,
    Source
    )
from .exceptions import CommandFailed

_logger = logging.getLogger("pydeploy.env")

class PythonEnvironment(object):
    def __init__(self, argv=()):
        super(PythonEnvironment, self).__init__()
        self._argv = list(argv)
        self.installer = Installer(self)
        self.utils = EnvironmentUtils(self)
        self._aliases = {}
        self._executed_deployment_file_locations = set()
        self._executed_deployment_file_hashes    = set()
    def add_alias(self, name, source):
        self._aliases[name] = source
    def has_alias(self, name):
        if isinstance(name, pkg_resources.Requirement):
            name = name.unsafe_name
        return name in self._aliases
    def checkout(self, source, *args, **kwargs):
        """
        Downloads a package from *source*, and returns the path to which it was extracted.
        """
        source = self._make_source_object(source)
        _logger.info("Checking out %r (%s)", source.get_name(), type(source).__name__)
        source = self._make_source_object(source)
        return source.checkout(self, *args, **kwargs)
    def create_and_activate(self):
        raise NotImplementedError() # pragma: no cover
    def execute_deployment_file_once(self, path_or_url):
        executed = False
        if path_or_url not in self._executed_deployment_file_locations:
            content = self._get_deployment_file_content(path_or_url)
            content_hash = sha512(make_bytes(content)).digest()
            if content_hash not in self._executed_deployment_file_hashes:
                self.execute_deployment_string(content)
                self._executed_deployment_file_hashes.add(content_hash)
                executed = True
            self._executed_deployment_file_locations.add(path_or_url)
        if not executed:
            _logger.info("Deployment file at %r already executed. Skipping...", path_or_url)
    def execute_deployment_file(self, path_or_url):
        self.execute_deployment_string(self._get_deployment_file_content(path_or_url))
    def execute_deployment_file_url(self, url):
        _logger.info("Executing deployment file from url %r...", url)
        self.execute_deployment_file_object(os_api.urlopen(url))
    def execute_deployment_file_object(self, fileobj, filename=None):
        return self.execute_deployment_string(fileobj.read(), filename=filename)
    def execute_deployment_string(self, content, filename=None):
        executed_locals = self._get_config_file_locals(filename)
        exec(content, executed_locals)
    def execute_deployment_file_path(self, path):
        _logger.info("Executing deployment file %r...", path)
        with open(path, "rb") as fileobj:
            with self._filename_as_argv0(path):
                self.execute_deployment_file_object(fileobj, filename=path)
    def _get_deployment_file_content(self, path_or_url):
        if self._is_url(path_or_url):
            return os_api.urlopen(path_or_url).read()
        return open(path_or_url).read()
    def execute_deployment_stdin(self):
        _logger.info("Executing deployment script from standard input...")
        self.execute_deployment_file_object(sys.stdin, filename="<stdin>")
    @contextmanager
    def _filename_as_argv0(self, path):
        old_argv = self.get_argv()
        try:
            self._argv.insert(0, path)
            yield
        finally:
            self._argv = old_argv

    def install(self, source, reinstall=True):
        """
        Installs a package from *source*.

        @param reinstall: If False, skips installation if this source has already been installed.
        """
        with self.installer.get_installation_context():
            source = self._make_source_object(source)
            _logger.info("Installing %r (%s)", source.get_name(), type(source).__name__)
            if not self._is_already_installed(source) or reinstall:
                returned = source.install(self, reinstall=reinstall)
                self._post_install(source)
                return returned
    def get_argv(self):
        return list(self._argv)
    def get_checkout_cache(self):
        raise NotImplementedError() # pragma: no cover
    def get_path(self):
        raise NotImplementedError() # pragma: no cover
    def get_python_executable(self):
        raise NotImplementedError() # pragma: no cover
    def execute_pip_install(self, source, reinstall):
        raise NotImplementedError() # pragma: no cover
    def execute_easy_install(self, source, reinstall):
        raise NotImplementedError() # pragma: no cover
    def _execute(self, cmd):
        return command.execute_assert_success(cmd, shell=True)
    def _get_config_file_locals(self, filename):
        returned = dict(
            env = self,
            )
        if filename is not None:
            returned.update(__file__=filename)
        returned.update(get_all_sources_dict())
        for module_name in ['sys', 'os']:
            returned[module_name] = __import__(module_name)
        return returned
    def _is_already_installed(self, source):
        raise NotImplementedError() # pragma: no cover
    def _is_url(self, path_or_url):
        return bool(urlparse(path_or_url).scheme)
    def _make_source_object(self, source):
        if isinstance(source, pkg_resources.Requirement):
            specs = source.specs
            source = source.unsafe_name
        else:
            specs = []
        if isinstance(source, basestring) and source in self._aliases:
            source = self._aliases[source]
        if specs:
            source = source.resolve_constraints(specs)
        source = Source.from_anything(source)
        return source
    def _post_install(self, source):
        self._fix_sys_path()
    def _fix_sys_path(self):
        new_sys_path = self._get_new_sys_path()
        for new_path in set(new_sys_path) - set(sys.path):
            sys.path.insert(0, new_path)
            pkg_resources.fixup_namespace_packages(new_path)
    def _get_new_sys_path(self):
        result, output = self._execute("{} -c 'import sys;print sys.path'".format(self.get_python_executable()))
        return ast.literal_eval(output)

class Environment(PythonEnvironment):
    def __init__(self, path, argv=()):
        super(Environment, self).__init__(argv)
        self._path = os.path.abspath(path)
        self._checkout_cache = None
        self._states = []
    def get_path(self):
        return self._path
    def get_checkout_cache(self):
        return self._checkout_cache
    def create_and_activate(self):
        self._push_python_state()
        virtualenv_api.create_environment(self._path)
        self._checkout_cache = CheckoutCache(self._path)
        self._try_load_installed_signatures()
        self._activate()
        set_active_environment(self)
    def _activate(self):
        virtualenv_api.activate_environment(self._path)
    def deactivate(self):
        self._pop_python_state()
    def _push_python_state(self):
        state = dict(
            prefix = sys.prefix,
            path   = sys.path[:],
            modules = sys.modules.copy(),
            active_environment = get_active_envrionment(),
            )
        if hasattr(sys, 'old_prefix'):
            state['old_prefix'] = sys.old_prefix
        self._states.append(state)
    def _pop_python_state(self):
        state = self._states.pop(-1)
        if 'old_prefix' in state:
            sys.old_prefix = state.pop('old_prefix')
        elif hasattr(sys, "old_prefix"):
            del sys.old_prefix
        sys.prefix     = state.pop('prefix')
        set_active_environment(state.pop('active_environment'))
        sys.modules.clear()
        sys.modules.update(state.pop('modules'))
        sys.path[:] = state.pop('path')
        assert not state
    def execute_pip_install(self, source, reinstall):
        self._execute("{0} install {1}".format(self._get_pip_executable(), source))
    def execute_easy_install(self, source, reinstall):
        self._execute("{0} {1}".format(self._get_easy_install_executable(), source))
    def _get_pip_executable(self):
        return os.path.join(self._get_bin_dir(), "pip")
    def _get_easy_install_executable(self):
        return os.path.join(self._get_bin_dir(), "easy_install")
    def get_python_executable(self):
        return os.path.join(self._get_bin_dir(), "python")
    def _get_bin_dir(self):
        return os.path.join(self._path, "bin")
    #installation
    def _post_install(self, source):
        super(Environment, self)._post_install(source)
        self._mark_installed(source)
    def _get_site_dir(self):
        # taken from virtualenv's activate_this.py...
        if sys.platform == 'win32':
            return os.path.join(self._path, 'Lib', 'site-packages')
        return os.path.join(self._path, 'lib', 'python%s' % sys.version[:3], 'site-packages')
    #signatures
    def _is_already_installed(self, source):
        return source.get_signature() in self._installed
    def _mark_installed(self, source):
        self._installed.append(source.get_signature())
        self._saved_installed_signatures()
    def _saved_installed_signatures(self):
        with open(self._get_temporary_installed_signatures_filename(), "wb") as f:
            pickle.dump(self._installed, f)
        os.rename(self._get_temporary_installed_signatures_filename(),
                  self._get_installed_signatures_filename())
    def _try_load_installed_signatures(self):
        try:
            self._load_installed_signatures()
        except IOError:
            self._installed = []
    def _load_installed_signatures(self):
        with open(self._get_installed_signatures_filename(), "rb") as f:
            self._installed = pickle.load(f)
    def _get_installed_signatures_filename(self):
        return os.path.join(self._path, ".installed_signatures")
    def _get_temporary_installed_signatures_filename(self):
        return self._get_installed_signatures_filename() + ".tmp"

class GlobalEnvironment(PythonEnvironment):
    _checkout_cache = None
    def create_and_activate(self):
        self._checkout_cache = CheckoutCache(self._get_pydeploy_dir())
    def execute_easy_install(self, source, reinstall):
        return self._execute("easy_install {0} {1}".format("-U" if reinstall else "", source))
    def execute_pip_install(self, source, reinstall):
        return self._execute("pip install {0} {1}".format("-U" if reinstall else "", source))
    def get_checkout_cache(self):
        return self._checkout_cache
    def get_python_executable(self):
        return sys.executable
    def _is_already_installed(self, source):
        return False # let easy_install take care of it for now
    def _get_pydeploy_dir(self):
        return os.path.expanduser("~/.pydeploy")

_active_environment = None

def clear_active_environment():
    set_active_environment(None)

def get_active_envrionment():
    return _active_environment

def set_active_environment(e):
    global _active_environment
    _active_environment = e
