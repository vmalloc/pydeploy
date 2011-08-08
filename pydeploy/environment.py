import cPickle as pickle
import os
import sys
import logging
import subprocess
from contextlib import contextmanager
from urlparse import urlparse
from . import command
from . import os_api
from . import virtualenv_api
from .environment_utils import EnvironmentUtils
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
        self.utils = EnvironmentUtils(self)
    def checkout(self, source, *args, **kwargs):
        source = self._make_source_object(source)
        _logger.info("Checking out %r (%s)", source.get_name(), type(source).__name__)
        source = self._make_source_object(source)
        return source.checkout(self, *args, **kwargs)
    def create_and_activate(self):
        raise NotImplementedError() # pragma: no cover
    def execute_deployment_file(self, path_or_url):
        if self._is_url(path_or_url):
            self.execute_deployment_file_url(path_or_url)
        else:
            self.execute_deployment_file_path(path_or_url)
    def execute_deployment_file_url(self, url):
        _logger.info("Executing deployment file from url %r...", url)
        self.execute_deployment_file_object(os_api.urlopen(url))
    def execute_deployment_file_object(self, fileobj, filename=None):
        executed_locals = self._get_config_file_locals(filename)
        exec fileobj.read() in executed_locals
    def execute_deployment_file_path(self, path):
        _logger.info("Executing deployment file %r...", path)
        with open(path, "rb") as fileobj:
            with self._filename_as_argv0(path):
                self.execute_deployment_file_object(fileobj, filename=path)
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
        source = self._make_source_object(source)
        _logger.info("Installing %r (%s)", source.get_name(), type(source).__name__)
        if not self._is_already_installed(source) or reinstall:
            returned = source.install(self)
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
    def execute_pip_install(self, *args):
        raise NotImplementedError() # pragma: no cover
    def execute_easy_install(self, *args):
        raise NotImplementedError() # pragma: no cover
    def _execute(self, cmd):
        command.execute_assert_success(cmd, shell=True)
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
        return Source.from_anything(source)
    def _post_install(self, source):
        raise NotImplementedError() # pragma: no cover

class Environment(PythonEnvironment):
    def __init__(self, path, argv=()):
        super(Environment, self).__init__(argv)
        self._path = os.path.abspath(path)
        self._checkout_cache = None
    def get_path(self):
        return self._path
    def get_checkout_cache(self):
        return self._checkout_cache
    def create_and_activate(self):
        virtualenv_api.create_environment(self._path)
        self._checkout_cache = CheckoutCache(self._path)
        self._try_load_installed_signatures()
        virtualenv_api.activate_environment(self._path)
        set_active_environment(self)
    def execute_pip_install(self, source):
        self._execute("{0} {1}".format(self._get_pip_executable(), source))
    def execute_easy_install(self, source):
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
        virtualenv_api.activate_environment(self._path)
        self._mark_installed(source)
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
    def execute_easy_install(self, source):
        return self._execute("easy_install {0}".format(source))
    def execute_pip_install(self, source):
        return self._execute("pip install {0}".format(source))
    def get_checkout_cache(self):
        return self._checkout_cache
    def get_python_executable(self):
        return sys.executable
    def _post_install(self, source):
        pass
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
