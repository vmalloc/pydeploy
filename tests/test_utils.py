import os
import itertools

_UNIQUE_PACKAGE_NAMES = ("unique_package__{}".format(x) for x in itertools.count())
_EXPECTED_VALUES = itertools.count(1337)

def create_installable_package(path, name=None, reqs=()):
    if name is None:
        name = next(_UNIQUE_PACKAGE_NAMES)
    with open(os.path.join(path, "setup.py"), "w") as setup_file:
        _write_setup_file(setup_file, reqs=reqs, package_name=name)
    value = next(_EXPECTED_VALUES)
    os.makedirs(os.path.join(path, name))
    with open(os.path.join(path, name, "__init__.py"), "w") as module:
        module.write("value = {!r}".format(value))
    return Package(name, value)

def _write_setup_file(setup_file, package_name, reqs):
    setup_file.write(_SETUP_FILE_SKELETON.format(
        package_name=package_name,
        reqs=reqs
        ))

_SETUP_FILE_SKELETON = """\
from setuptools import setup, find_packages

setup(name={package_name!r},
      version="0.0.1",
      packages=find_packages(),
      install_requires={reqs},
      )
"""
class Package(object):
    def __init__(self, name, value):
        super(Package, self).__init__()
        self.name = name
        self.value = value
