import cPickle as pickle
import os
import subprocess
from urlparse import urlparse
from urllib2 import urlopen
from virtualenv import create_environment
from .utils import execute_assert_success
from .checkout_cache import CheckoutCache
from .sources import (
    get_all_sources_dict,
    PIP,
    Path,
    Source
    )
from .exceptions import CommandFailed

class Environment(object):
    def __init__(self, path):
        super(Environment, self).__init__()
        self._path = os.path.abspath(path)
        self.checkout_cache = CheckoutCache(self._path)
    def create_and_activate(self):
        create_environment(self._path)
        self._try_load_installed_signatures()
        self._activate()
    def _activate(self):
        activate_script_path = os.path.join(self._path, "bin", "activate_this.py")
        execfile(activate_script_path, dict(__file__ = activate_script_path))
    def execute_deployment_file(self, path_or_url):
        if self._is_url(path_or_url):
            self.execute_deployment_file_url(path_or_url)
        else:
            self.execute_deployment_file_path(path_or_url)
    def _is_url(self, path_or_url):
        return bool(urlparse(path_or_url).scheme)
    def execute_deployment_file_url(self, url):
        self.execute_deployment_file_object(urlopen(url))
    def execute_deployment_file_path(self, path):
        with open(path, "rb") as fileobj:
            self.execute_deployment_file_object(fileobj)
    def execute_deployment_file_object(self, fileobj):
        executed_locals = self._get_config_file_locals()
        exec fileobj.read() in executed_locals
    def _get_config_file_locals(self):
        returned = dict(
            env = self,
            )
        returned.update(get_all_sources_dict())
        for module_name in ['sys', 'os']:
            returned[module_name] = __import__(module_name)
        return returned
    def _get_python_executable(self):
        return os.path.join(self.get_bin_dir(), "python")
    def get_bin_dir(self):
        return os.path.join(self._path, "bin")
    #installation
    def install(self, source, reinstall=True):
        source = self._make_source_object(source)
        if not self._is_already_installed(source) or reinstall:
            print "INSTALLING!!!"
            returned = source.install(self)
            self._mark_installed(source)
            return returned
    def checkout(self, source):
        source = self._make_source_object(source)
        return source.checkout(self)
    def _make_source_object(self, source):
        if isinstance(source, basestring) and os.path.exists(source):
            source = Path(source)
        if not isinstance(source, Source):
            source = PIP(source)
        return source
    def _run_local_python(self, argv, cwd):
        cmd = list(argv)
        cmd.insert(0, self._get_python_executable())
        execute_assert_success(cmd, shell=False, cwd=cwd)
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
    #execution
    def execute_script(self, script, *args, **kwargs):
        argv = [self._get_python_executable(), os.path.join(self.get_bin_dir(), script)]
        argv.extend(args)
        return subprocess.call(argv, **kwargs)
    def execute_script_assert_success(self, *args, **kwargs):
        returned = self.execute_script(*args, **kwargs)
        if returned != 0:
            raise CommandFailed()
        return returned
