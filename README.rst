Introduction
============
pydeploy is a lightweight utility for bootstrapping and deploying *virtualenv* environments. The main target of pydeploy is not building complex solutions (like zc.buildout, for instance), but rather establishing isolated installations of python software pieces, including dependencies.

pydeploy utilizes *virtualenv* as the backend for creating the python installation.

Currently pydeploy supports installing from either *git*, *url*, or *local directory*.

Getting Started
===============
pydeploy relies on *definition files* to control the setup. Let's assume we have a local package in '/path/to/local/package', which relies on 'http://path/to/dependency.tgz' and on the package available from git 'git://some/url/to/package' (both not available to the world). All packages are structured like normal python packages, i.e. with *setup.py* scripts and *install_requires* metadata.

Below is the file we will use, let's call it deploy.py:
::

  env.install_from_url("http://path/to/dependency.tgz")
  env.install_from_git("git://some/url/to/package")
  env.install_from_dir("/path/to/package")

And that's it!

Any line we append after the last line above will run in the new environment (paths are modified and all). We can, for instance, run scripts afterwards, using the shortcuts *execute_script* and *execute_script_assert_success*
::

  env.execute_script("my_script", "arg1", "arg2")
  env.execute_script_assert_success("my_script")

To run our config file, we simply execute:
::

  pydeploy /path/to/deploy.py ./deployment

You can even serve the file through http:
::

  pydeploy http://my_server.com/path/to/deploy.py

Documentation
=============

Initializing the Environment
----------------------------
Normally the deployment environment is initialized for you, but you can also initialize it yourself:
::

  from pydeploy.environment import Environment
  env = Environment('your/path')
  env.create_and_activate()

Installing Packages
-------------------
::

  # from a directory with setup.py in it
  env.install_from_dir("/path/to/dir")
  # pass blindly to pip
  env.install_using_pip("pydeploy>=0.0.1")
  # URL of a compressed package, with setup.py inside
  env.install_from_url("http://some.url.com/package.tgz")
  # install using git
  env.install_from_git("git://some.git.repo/package.git")

  # checkout from git, then do stuff before installing
  path = env.checkout_from_git("git://some.git.repo/package.git")
  _modify_files_as_you_want(path)
  env.install_from_dir(path)
  


