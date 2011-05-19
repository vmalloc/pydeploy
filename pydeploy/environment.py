import os
import subprocess
from urlparse import urlparse
from urllib2 import urlopen
from virtualenv import create_environment
from .utils import execute_assert_success
from .checkout_cache import CheckoutCache
from .sources import get_all_sources_dict, Source
from .exceptions import CommandFailed

class Environment(object):
    def __init__(self, path):
        super(Environment, self).__init__()
        self._path = os.path.abspath(path)
        self.checkout_cache = CheckoutCache(self._path)
    def create_and_activate(self):
        create_environment(self._path)
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
        import pdb
        pdb.set_trace()
        for module_name in ['sys', 'os']:
            returned[module_name] = __import__(module_name)
        return returned
    def _get_python_executable(self):
        return os.path.join(self.get_bin_dir(), "python")
    def get_bin_dir(self):
        return os.path.join(self._path, "bin")
    #installation
    def install(self, source):
        source = self._make_source_object(source)
        source.install(self)
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
    #execution
    def execute_script(self, script, *args):
        argv = [self._get_python_executable(), os.path.join(self.get_bin_dir(), script)]
        argv.extend(args)
        return subprocess.call(argv, close_fds=True)
    def execute_script_assert_success(self, *args):
        returned = self.execute_script(*args)
        if returned != 0:
            raise CommandFailed()
        return returned