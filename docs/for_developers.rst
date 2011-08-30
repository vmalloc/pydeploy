.. developers:

For Developers / Package Maintainers
------------------------------------

Writing Pydeploy Files
======================

A "pydeploy file" is simply a Python script that can be executed by pydeploy. If you write a file -- **test.py** -- containing the following::

 print "hello"

And execute it using::

 pydeploy run test.py

You'll simply see the "hello" message printed out. What distinguishes pydeploy scripts from normal Python files is that they get a special variable in their available namespace -- the **env** object, pointing to the :py:class:`.PythonEnvironment` class. The environment represents the current Python installation which we're working on. The basic entry point to it is :py:meth:`.PythonEnvironment.install`. This method receives a *source* to install, which can be many things::

  env.install(URL("http://path/to/dependency.tgz"))
  env.install(SCM("git://some/url/to/package"))
  env.install("/path/to/package")

Accepted sources are:

* Path (default): local path to the package
* EasyInstall (default if argument is not a path and not a URL): for installing using easy_install
* PIP: install using pip
* SCM: for installing from source repository
* URL: for installing from the web

Now once you run your file, you'll trigger the installation of these packages in your environment (whether global or a virtual environment).

Using Pydeploy Files when Installing Packages
=============================================
Pydeploy is mostly useful when used to install packages. In this scenario, you do not execute a pydeploy file directly, but rather use pydelpoy's *install* command to install a package.

Whenever a package contains a file called *pydeploy_setup.py* (located next to its *setup.py* file), it will be run by pydeploy prior to actually installing the package.

This rule applies recursively. Let's say that we have a package *A*, that depends on package *B*, stored locally in a git repository. Furthermore let's say *B* depends on *C* in a different repository. You can write the following *pydeploy_setup.py* in *A*::

 env.install("git://path.to.server/for/B.git")

And in turn, write the following *pydeploy_setup.py* in *B*::

 env.install("git://another.path.to/C.git")

When you install package *A* (regardless of where from), pydeploy will::

 1. run the pydeploy_setup for A
 2. follow the install() call to download and install B
 3. prior to B's installation, it will execute B's pydeploy_setup.py
 4. C will be downloaded and installed
 5. B will be installed
 6. A will be installed

Installing Dependencies Through *install_requires*
==================================================
When installing from sources other than *easy_install* or *pip*, pydeploy can extract the names of the packages which are dependencies of the package being installed. By default this information is not used, but you can *alias* a package name to a specific source, making the *install_requires* feature work for you.

Let's take a simple case of a package *A* depending on *B* and *C*. Let's also assume that *B* and *C* each in turn depend on *D*. We don't want to repeat *D*'s URL in both setup files of B and C, but we still have to make the installation work. How do we make that happen?

We'll create a common file in a central location. This central location can be an SCM server, a network share, or a config file in the user's homedir, whichever best suits you. Let's call it *pydeploy_aliases.py*::

  env.add_alias("A", "/path/to/a/")
  env.add_alias("B", "http://bla.com/B.tgz")
  env.add_alias("C", "git://git.server.for/C.git")
  env.add_alias("D", "http://download.server.for/D.tgz")

The file uses the :py:meth:`.add_alias` method to let pydeploy know that the package name 'X' refers actually to a custom source, rather than to PyPI's index.
  
And now all we need to do is point our *pydeploy_setup.py* files to that alias file. We use :py:meth:`.execute_deployment_file_once` for that::

  # in each pydeploy_setup.py:
  env.execute_deployment_file_once("http://download.server.for/pydeploy_aliases.py")

Now when installing A, pydeploy will analyze its dependencies, detect B and C (which it now knows are aliases) and install them. In the process it will also detect D and install it according to its alias.

Misc. Utilities
===============

SSH Remote Deployment
+++++++++++++++++++++
The *pydeploy.remote* utility module provides a manner for deploying a script remotely.
::

  from pydeploy.remote import deploy_via_ssh
  return_code = deploy_via_ssh("hostname", "http://pydeploy_file_url", "/tmp/deployment_dir")

The *deploy_via_ssh* utility can also receive file objects with the script to run, as a convenience:
::

  from pydeploy.remote import deploy_via_ssh
  from cStringIO import StringIO
  return_code = deploy_via_ssh("hostname", StringIO("print 'source here!'"), "/tmp/deployment_dir")

  
