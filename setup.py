import os
import itertools
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "pydeploy", "__version__.py")) as version_file:
    exec(version_file.read())

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
      version=__version__,
      packages=find_packages(exclude=["tests"]),
      install_requires=["virtualenv", "pip", "pyforge", "infi.unittest"],
      entry_points = dict(
          console_scripts = "pydeploy = pydeploy.entry_points.pydeploy:main"
          )
      )
