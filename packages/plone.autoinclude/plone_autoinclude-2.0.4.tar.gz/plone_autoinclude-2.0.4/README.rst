.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

.. image:: https://coveralls.io/repos/github/plone/plone.autoinclude/badge.svg?branch=main
    :target: https://coveralls.io/github/plone/plone.autoinclude?branch=main
    :alt: Coveralls

.. image:: https://img.shields.io/pypi/l/plone.autoinclude.svg
    :target: https://pypi.org/project/plone.autoinclude/
    :alt: License


=================
plone.autoinclude
=================

Automatically include zcml of a package when it is loaded in a Plone site.

Features
--------

- It is an alternative to ``z3c.autoinclude``.
- When a package registers an autoinclude entry point, we load its Python code at Zope/Plone startup.
- And we load its zcml.
- Works with Buildout-installed packages.
- Works with pip-installed packages.


Compatibility
-------------

Since Plone 6.0.0a2 this package is included in core Plone.
See `PLIP 3339 <https://github.com/plone/Products.CMFPlone/issues/3339>`_.

The 1.x versions also work on Plone 5.2, on Python 3.6+.


For add-on authors
------------------

When you have an existing package that has some zcml, you probably already have something like this in your ``setup.py``::

    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """

or in a dictionary::

    entry_points={
        "z3c.autoinclude.plugin": [
            "target = plone",
        ],
    }

or in ``setup.cfg``::

    [options.entry_points]
    z3c.autoinclude.plugin =
        target=plone

This still works!
You do not need to change anything.

But if you do not care about compatibility with ``z3c.autoinclude``, you could use this new entry point::

    entry_points="""
    [plone.autoinclude.plugin]
    target = plone
    """

It does the same thing, but it only works with ``plone.autoinclude``.

Note: you should *not* add ``plone.autoinclude`` in your ``install_dependencies``.
It is the responsibility of the framework (usually Plone) to do this.


Entry point details
-------------------

This is an entry point with all options specified::

    entry_points="""
    [plone.autoinclude.plugin]
    target = plone
    module = example.alternative
    """

You must specify at least one option, otherwise the entry point does not exist.

``target``
    In which framework should your zcml be loaded?
    For a Plone add-on you would use ``plone``.
    If Zope ever wants to use something similar, it could add configuration to look for packages with ``target="zope"``.
    You can come up with targets yourself, and load them in a policy package, maybe: cms, frontend, companyname, customername, nl/de (language).
    If target is empty, or the option is not there, the zcml will get loaded by all frameworks.

``module``
    Use this when your package name is different from what you import in Python.
    See also the next section.


Different project and module name
---------------------------------

Usually the project name of an add-on (what is in ``setup.py`` or ``setup.cfg``) is the same as how you would import it in Python code.
It could be different though.
In that case, you may get a ``ModuleNotFoundError`` on startup: ``plone.autoinclude`` tries to import the project name and this fails.

This may happen more often since ``setuptools`` 75.8.1, which changed some name handling to be in line with the standards in several packaging-related PEPs (Python Enhancement Proposals).

The easiest way to solve this, is to switch from ``z3c.autoinclude.plugin`` to ``plone.autoinclude.plugin``, if you have not done so already,
and specify the module.
In ``setup.py``::

    setup(
        name="example.different2",
        entry_points="""
        [plone.autoinclude.plugin]
        module = example.somethingelse2
        """,
    )

If you must still support Plone 5.2 and are tied to ``z3c.autoinclude.plugin``, or if you cannot edit the problematic package, you can work around it.
You set an environment variable ``AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR``.
To accept ``ModuleNotFoundError`` in all packages::

    export AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR=1

To accept ``ModuleNotFoundError`` only in specific packages, use a comma-separated list of project names, with or without spaces::

    export AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR=example.different,example.different2

In the logs you will see a traceback so you can investigate, but startup continues.
You should make sure the zcml of this package is loaded in some other way.


Comparison with ``z3c.autoinclude``
-----------------------------------

- ``z3c.autoinclude`` supports ``includeDependencies`` in a zcml file in your package.
  This would look in the ``setup_requires`` of the package to find dependencies.
  For each, it would load the zcml.
  This can take quite long.
  It might not work for packages installed by ``pip``, but this is not confirmed.
  In the Plone community this is discouraged, and Plone already disables this in the tests.
  ``plone.autoinclude`` does not support this.
  You should load the zcml of the dependencies explicitly in the ``configure.zcml`` of your package.
- ``z3c.autoinclude`` tries hard to find packages in non-standard places, installed in weird or old ways,
  or with a module name that differs from the package name, with code especially suited for eggs that buildout installs.
  ``plone.autoinclude`` simply uses ``importlib.import_module`` on the module name.
  If there is a mismatch between package name and module name, you can set ``module = modulename`` in your entry point.
- ``z3c.autoinclude`` does not support empty targets.
  The target of the entry point must match the target that is being loaded.
  ``plone.autoinclude`` *does* support empty targets: they will always get loaded.
  This is not good or bad, it is just a different choice.
- ``z3c.autoinclude`` supports disabling loading the plugins, via either an environment variable or an api call.
  ``plone.autoinclude`` does not.
  But ``Products.CMFPlone`` currently loads the ``z3c.autoinclude`` plugins unless a zcml condition is true: ``not-have disable-autoinclude``.
  When ``Products.CMFPlone`` switches to ``plone.autoinclude``, it can use this same condition.

In general, ``plone.autoinclude`` is a bit more modern, as it only started in 2020, and only supports Python 3.


Usage in Plone 5.2
------------------

For instructions on how to use this in Plone 5.2, see the ``README.rst`` of any 1.x version of this package.


For other frameworks
--------------------

If you want to use this in a framework that is built on top of Zope, but is not Plone, you need to take care of the following:

- Include the ``plone.autoinclude`` package in ``install_requires``.
- In your ``meta.zcml`` load the ``meta.zcml`` of ``plone.autoinclude``.
- In your ``meta.zcml`` load the ``meta.zcml`` of your plugins:
  ``<autoIncludePlugins target="your-framework" file="meta.zcml" />``
- In your ``configure.zcml`` load the ``configure.zcml`` of your plugins:
  ``<autoIncludePlugins target="your-framework" file="configure.zcml" />``
- In your ``overrides.zcml`` load the ``meta.zcml`` of your plugins in override mode:
  ``<autoIncludePluginsOverrides target="your-framework" file="meta.zcml" />``


Contribute or get support
-------------------------

- If you are having issues, please let us know in the issue tracker: https://github.com/plone/plone.autoinclude/issues
- The source code is on GitHub: https://github.com/plone/plone.autoinclude


License
-------

The project is licensed under the GPLv2.
