Introduction
============
pydeploy is a lightweight utility for bootstrapping and deploying *virtualenv* environments. The main target of pydeploy is not building complex solutions (like zc.buildout, for instance), but rather establishing isolated installations of python software pieces, including dependencies.

pydeploy utilizes *virtualenv* as the backend for creating the python installation.

Currently pydeploy supports installing from either *git*, *url*, or *local directlry*.

Getting Started
===============
pydeploy relies on *definition files* to control the setup. Let's assume we have a local package in '/path/to/local/package', which relies on 'http://path/to/dependency.tgz' and on the package available from git 'git://some/url/to/package' (both not available to the world). All packages are structured like normal python packages, i.e. with *setup.py* scripts and *install_requires* metadata.

Below is the file we will use, let's call it deploy.py:
::

  env.install_from_url("http://path/to/dependency.tgz")
  env.install_from_git("git://some/url/to/package")
  env.install_from_http("/path/to/package")

And that's it!

Any line we append after the last line above will run in the new environment (paths are modified and all). We can, for instance, run scripts afterwards, using the shortcuts *execute_script* and *execute_script_assert_success*
::

  env.execute_script("my_script", "arg1", "arg2")
  env.execute_script_assert_success("my_script")
