
import os
import itertools
from setuptools import setup, find_packages

from pydeploy import __version__ as VERSION

setup(name="pydeploy",
      classifiers = [
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python :: 2.6",
          ],
      description="Library for bootstrapping Python environments",
      license="BSD",
      author="Rotem Yaari",
      author_email="vmalloc@gmail.com",
      version=VERSION,
      packages=find_packages(exclude=["tests"]),
      install_requires=["virtualenv", "pip"],
      scripts=["scripts/pydeploy"],
      )
