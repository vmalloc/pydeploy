Pydeploy Overview
-----------------

The Problem
===========

Python is a great language and development platform, constantly gaining enormous popularity in various fields of the industry.

Any software development platform (and languages/interpreters in particular) need to provide their developers with means to reuse code that was written elsewhere. In most cases this is done in the form of *modules* (or *packages*). It is generally agreed that software components should be decomposed and granularized so that each package is reusable in as many contexts as possible, while still being coherent and maintainable.

However, an inherent problem stems from this - how do you keep track of all the packages and modules that your code needs? If you want to use a specific library **X**, how do you make sure you install it properly, so that all of its dependencies are intact?

This issue of distribution and installation is very important, and each platform addresses it individually. When focusing on Python specifically, we can see that there's far from one golden solution. A quick count shows:

* `Distutils <http://docs.python.org/library/distutils.html>`_ -- Python's original, out-of-the-box packaging and distribution solution
* `setuptools <http://pypi.python.org/pypi/setuptools>`_ -- Enhances distutils, and adds the *easy_install* tool for automatic installation from pypi
* `distribute <http://pypi.python.org/pypi/distribute>`_ -- a fork of setuptools (and a drop-in replacement). It is related to the *pip* tool, which is a replacement for some of the uses of *easy_install*.

These tools work great (in general) if you're distributing something that will be available on the internet through the `PyPI <http://pypi.python.org>`_ indexing site. Your **setup.py** file can include requirements identified by project names and versions, and *easy_install* / *pip* take care of installing all dependencies from PyPI.

However, erious hassle forms when you try to deploy packages that are written in-house, without being published. If you have plenty of packages, some arriving from the outside world and some arriving from within your organization, you're stuck, because the same mechanism cannot work here (more on that in a second).

Even if you do solve the installation issue, there is another issue of *deployment*. For example, in some cases it might not be enough to just run **easy_install my_package**:

* You might not have permissions to run easy_install (in many cases the global easy_install requires root permissions), in which case you might need a `virtual environment <http://pypi.python.org/pypi/virtualenv>`.
* You might want to run some more tools or scripts on the environment after the installation (for instance, run automated tests, servers or what not)
* You might want to do different actions depending on the platform on which you're installing.

All the tools mentioned above are not very easily automatable, so assuming you want to use Python and not some variant of shell scripting, the deployment tasks become inconvenient.

Possible Solutions
==================

A Custom PyPI Server
++++++++++++++++++++
This approach generally works in many places, but is very error-prone. It is mostly intended to solve the installation issue, rather than the deployment issue.

In this scheme you establish a server inside your organization that mimicks **PyPI**. You then register your internal packages to that server, and pass a flag to *easy_install* to install from that repository.

**However**, although installing from such a server is very simple (and not error prone, because at the worst case you simply won't find your package), distributing internal packages through this mechanism is simply unacceptable as a solution. In order to register and/or upload your package you need a .pypirc file. If you get any field of that file wrong (which is quite easy, I assure you), you'll silently be defaulted to the global pypi server.

Assuming you distribute packages to both the internet and the internal organization, you'll soon end up accidentally publishing internal packages. Yikes.

Also, if you cache packages in the local mimicking server, you start dealing with inconsistencies once the global packages get updated, which is also not desirable.

pip
+++

Pip technically has the capability of installing directly from source code repositories and from URLs. However, eventually it still executes the same logic as *easy_install*, meaning that it will be difficult and obscure to declare dependencies from internal projects in your setup.py file.

Pip also doesn't take care of the deployment part.

zc.buildout
+++++++++++
`zc.buildout <http://pypi.python.org/pypi/zc.buildout>` is a complex project which acts as a mix between a build system, a deployment system and a virtual environment. It basically solves most of the problems mentioned above by defining an environment with a configuration file pointing to actions to be taken, and "recipes", dictating what to do for each action.

This would have been a magic bullet for the problems listed above - however, it is still far from perfect.

First, the learning curve is far from optimal. If you look for the documentation for zc.buildout, you'll stumble upon multiple sources, like `this <http://www.buildout.org/docs/tutorial.html>`_. However, the best source people are pointing to is `this one <http://pypi.python.org/pypi/zc.buildout/1.5.2>`_ (written for an older version), and from the length of it, you can see something is not right. The document uses mostly doctests to describe what's happening, but while doctests are great, they do a poor job at describing how to write a buildout configuration file.

Second, zc.buildout is extremely slow. If you have an environment you would like to constantly update, each build takes a lot of time, and can cross the 1 minute threshold in some cases.

Third, zc.buildout is extremely complex, and just like any complex project it has a lot of bugs that are not getting solved in time. You can see many people already working on forked versions of zc.buildout as their open issues don't get resolved. With all due respect to zc.buildout, the task we would like to perform is simpler, and makes it an overkill.

Pydeploy
========

Pydeploy tries to bridge the gap between installation and deployment, and at the same time provide a reasonable (although not perfect yet) mechanism for mixed in-house and public package management:

* Pydeploy "configuration" is actually a python script, so you are not confined to the syntax of a .ini file
* The simplest use case is the simple: **pydeploy install <package>**. No learning curve if you just want to install a single package from somewhere.

