from __future__ import print_function
from contextlib import contextmanager
from shutil import copyfileobj
from urllib2 import urlopen
from urlparse import urlparse
import hashlib
import os
import subprocess
import sys
import tarfile

_BOOTSTRAPPER_DIR = os.path.expanduser("~/.pydeploy")
_PACKAGE_DIR = os.path.join(_BOOTSTRAPPER_DIR, "packages")

def main():
    _import_or_fetch('virtualenv',
                     "http://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.6.1.tar.gz#md5=1a475df2219457b6b4febb9fe595d915")
    _import_or_fetch('pip',
                     "http://pypi.python.org/packages/source/p/pip/pip-1.0.1.tar.gz#md5=28dcc70225e5bf925532abc5b087a94b")
    _import_or_fetch('argparse',
                     'http://argparse.googlecode.com/files/argparse-1.2.1.tar.gz#md5=2fbef8cb61e506c706957ab6e135840c')
    _import_or_fetch('pydeploy',
                     "http://pypi.python.org/packages/source/p/pydeploy/pydeploy-0.0.6.tar.gz")
    return _exec_pydeploy()

def _import_or_fetch(module_name, package_url):
    try:
        __import__(module_name)
    except ImportError:
        _fetch_and_install(package_url)
        __import__(module_name)
        log("Installed {0}", module_name)
    else:
        log("{0} already installed", module_name)

def _fetch_and_install(url):
    urlinfo = urlparse(url)
    package_name = urlinfo.path.rsplit("/", 1)[-1]
    _ensure_dir(_PACKAGE_DIR)
    package_path = os.path.join(_PACKAGE_DIR, package_name)
    package_hash = urlinfo.fragment
    if package_hash:
        if not package_hash.startswith("md5="):
            raise ValueError("Unknown hash for {0}".format(url))
        package_hash = package_hash[4:]
    else:
        package_hash = None
    if not os.path.exists(package_path) or not _md5_matches(package_path, package_hash):
        log("Downloading {0}...", package_name)
        with open(package_path, "wb") as package:
            copyfileobj(urlopen(url), package)
    else:
        log("Using existing package at {0}", package_path)
    _install(package_path)
    return package_path

def _md5_matches(filename, hash):
    if hash is None:
        return True
    with open(filename, "rb") as infile:
        h = hashlib.md5(infile.read())
    return hash == h.hexdigest()

def _ensure_dir(d):
    if not os.path.isdir(d):
        os.makedirs(d)

def _install(package_path):
    if not os.path.isdir(package_path):
        package_path = _unzip(package_path)
    package_path = _get_setup_py_directory(package_path)
    sys.path.insert(0, package_path)

def _get_setup_py_directory(d):
    for dirname, dirnames, filenames in os.walk(d):
        if 'setup.py' in filenames:
            return dirname
    raise LookupError("No setup.py found!")

def _unzip(package_path):
    if package_path.endswith(".tar.gz") or package_path.endswith(".tgz"):
        t = tarfile.open(package_path, "r:gz")
    else:
        raise NotImplementedError()
    extract_path = os.path.join(_PACKAGE_DIR, "extracted", os.path.basename(package_path))
    _ensure_dir(extract_path)
    t.extractall(extract_path)
    return extract_path

def _exec_pydeploy():
    sys.argv[0] = 'pydeploy'
    from pydeploy.entry_points.pydeploy import main
    return main()

################################## Boilerplate #################################
_VERBOSE = True
def log(msg, *args, **kwargs):
    if _VERBOSE:
        if args or kwargs:
            msg = msg.format(*args, **kwargs)
        print(msg, file=sys.stderr)

if __name__ == '__main__':
    sys.exit(main())
