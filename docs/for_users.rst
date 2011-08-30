For Users (Quick Guide)
-----------------------

Installing a Package
====================
Installing a package with pydeploy is as easy as it gets::

  pydeploy install <package>

**package** can be either one of:

* a local package directory (containing a **setup.py** file)
* a URL of a package (compressed) to download and install
* a URL of an SCM repository (like git://some_hostname/repo)
* a name of a package to be searched in PyPI (in this case it's actually invokes *easy_install* under the hood).

.. note:: if you would like the package to be installed in a virtual environment (with virtualenv), you can use the **--env=path** flag to point it to your virtual environment directory.

Running a Configuration File
============================
In some cases pydeploy is used to run a file which dictates what steps are to be done. In this case you should just do::

  pydeploy run <file>

**file** can be either:

* a local file on your filesystem
* a URL to a file on a server somewhere

.. note:: the --env flag exists for the **run** command as well. It will execute the file in the context of the virtual environment specified. See :doc:`the next chapter <for_developers>` for more details.

Bootstrapping Pydeploy
======================

On hosts that don't have pydeploy installed (and perhaps installation is an issue due to permissions), a bootstrapper for pydeploy is available online:
::

  wget https://github.com/vmalloc/pydeploy/raw/master/scripts/bootstrapper.py
  python bootstrapper.py <args>

Where *args* are the argument you would pass to pydeploy. You can even do this in one line:  
::

  curl https://github.com/vmalloc/pydeploy/raw/master/scripts/bootstrapper.py | python - <args>

Or even shorter:
::

  curl -L bit.ly/ilTVUN | python - <args>
