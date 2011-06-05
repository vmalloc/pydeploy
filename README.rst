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

  env.install(URL("http://path/to/dependency.tgz"))
  env.install(SCM("git://some/url/to/package"))
  env.install("/path/to/package")

And that's it! After the activation, python code executes in the new environment.

To run our config file, we simply execute:
::

  pydeploy /path/to/deploy.py ./deployment

You can even serve the file through http:
::

  pydeploy http://my_server.com/path/to/deploy.py

On hosts that don't have pydeploy installed (and perhaps installation is an issue due to permissions), a bootstrapper is available online:
::

  curl https://github.com/vmalloc/pydeploy/raw/master/scripts/bootstrapper.py | python - <args>

Or even shorter:
::
  curl -L bit.ly/ilTVUN | python - <args>

Where *<args>* is the arguments passed to the pydeploy front-end.
  
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
Installing is done via the *.install()* method of the environment class, receiving the source object and an optional *reinstall* argument.

*Source* can be any of:

* Path (default): local path to the package
* EasyInstall (default if argument is not a path): for installing using easy_install
* PIP: install using pip
* SCM: for installing from source repository
* URL: for installing from the web

*reinstall* controls what happens if the directory is already installed. By default, it is true, so the packages get re-fetched (and thus possibly upgraded) on each deployment. For some sources (like pip) this can be very quick nevertheless, because detection is done to check if the version is satisfied.

Checking Out
------------
For some sources, you can perform a *checkout*, that is, fetching the package but not installing it, and returning the local path in which it is stored:
::

  path_to_package = env.checkout(SCM('git://some.git.repo/repo'))


Executing Scripts and Functions
-------------------------------
The pydeploy environment provides more utilities for performing basic tasks:

Run a python script (using our environment's python, of course):
::

  env.utils.execute_python_script("/path/to/my_script.py arg1 arg2")

This also accepts lists as commands:
::

  env.utils.execute_python_script(["/path/to/my_script.py", "arg1"])


Argument Passing
================
It is also possible for your deployment file to run a python functions before it finishes. pydeploy consumes arguments from the command line, so getting the 'clean' argv list can be done by the get_argv() method:
::

  import argparse
  my_parser = argparse.ArgumentParser(...)
  args = my_parser.parse_args(env.get_argv())


Advanced
--------

Automatic Remote Deployment
===========================
The *pydeploy.remote* utility module provides a manner for deploying a script remotely.
::

  from pydeploy.remote import deploy_via_ssh
  return_code = deploy_via_ssh("hostname", "http://pydeploy_file_url", "/tmp/deployment_dir")

The *deploy_via_ssh* utility can also receive file objects with the script to run, as a convenience:
::

  from pydeploy.remote import deploy_via_ssh
  from cStringIO import StringIO
  return_code = deploy_via_ssh("hostname", StringIO("print 'source here!'"), "/tmp/deployment_dir")

  
Known Issues
------------
* When using PIP to install a library that exists on the host, pip will not perform an actual installation. This means, for instance, that scripts will not be copied to the bin dir of the virtual environment. In such cases EasyInstall is recommended.
