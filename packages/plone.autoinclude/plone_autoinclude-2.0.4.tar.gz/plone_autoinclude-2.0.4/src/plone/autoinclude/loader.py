from importlib.metadata import distribution
from importlib.metadata import distributions
from importlib.metadata import PackageNotFoundError
from importlib.resources import files
from zope.configuration.xmlconfig import include
from zope.configuration.xmlconfig import includeOverrides

import importlib
import logging
import os
import re
import sys


if sys.version_info.major == 3 and sys.version_info.minor < 10:
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


logger = logging.getLogger(__name__)

# Dictionary of project names and packages that we have already imported.
_known_module_names = {}

# Maybe allow ModuleNotFoundError.
# This can be a boolean (0/1) or a list of project names (from setup.py),
# separated by comma.
AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR = os.getenv(
    "AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR", ""
)
ALLOW_MODULE_NOT_FOUND_SET = set()
ALLOW_MODULE_NOT_FOUND_ALL = False
try:
    ALLOW_MODULE_NOT_FOUND_ALL = bool(int(AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR))
except (ValueError, TypeError):
    _allowed = AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR.replace(" ", "").split(",")
    if _allowed:
        ALLOW_MODULE_NOT_FOUND_SET = set(_allowed)


def _get_module_name_from_project_name(project_name):
    """Get module name from project_name.

    We got the project_name from an entry point, so there should be a
    distribution that we can find with this name.

    From there, we want to get a module or package name.
    If we are lucky, this is the same as the project name, but it can differ.

    This must be something we can import.  So we at least replace any dashes
    with underscores.
    """
    try:
        dist = distribution(project_name)
    except PackageNotFoundError:
        # Recent setuptools versions normalize the project name
        # replacing `-_.` with dashes and then underscores.
        #
        # Before giving up, we try to do the same exact thing, see:
        # https://github.com/pypa/setuptools/blob/84b7b2a2f6eaf992aad6b5af923fa3f48ae7b566/setuptools/_vendor/importlib_metadata/__init__.py#L835-L839C16  # noqa: E501
        #
        dist = distribution(
            re.sub(r"[-_.]+", "-", project_name).lower().replace("-", "_")
        )

    # In Python 3.9, dist.name does not exist, or maybe not always.
    if hasattr(dist, "name"):
        dist_name = dist.name
    else:
        dist_name = dist.metadata["Name"]
    return dist_name.replace("-", "_")


def load_z3c_packages(target=""):
    """Load packages from the z3c.autoinclude.plugin entry points.

    After running the function, the packages have been imported.
    This returns a dictionary of package names and packages.
    """
    dists = {}
    for ep in entry_points().select(group="z3c.autoinclude.plugin"):
        # If we look for target 'plone' then only consider entry points
        # that are registered for this target (module name).
        # But if the entry point is not registered for a specific target,
        # we can include it.
        if target and ep.name == "target" and ep.value != target:
            continue
        # We should always be able to get the distribution.
        # Otherwise: how could we have an entry point?
        module_name = _get_module_name_from_project_name(ep.dist.name)
        if module_name not in _known_module_names:
            try:
                module = importlib.import_module(module_name)
            except ModuleNotFoundError:
                # Note: this may happen a lot, at least for z3c.autoinclude,
                # because the project name may not be the same as the package/module.
                # If we accept it, we may hide real errors though:
                # the module may be there but have an ImportError.
                # Second note: I am not sure how much this part is still needed
                # now that we call 'distribution(ep.dist.project_name)'.
                if (
                    not ALLOW_MODULE_NOT_FOUND_ALL
                    and module_name not in ALLOW_MODULE_NOT_FOUND_SET
                ):
                    logger.error(
                        f"Could not import {module_name}. Set environment variable "
                        "AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR=1 if you want to "
                        f"allow this. Or set it to '{module_name}' to only allow for "
                        "this project. Can be a comma-separated list of project "
                        "names. Or replace the z3c.autoinclude.plugin entry point of "
                        "this project with plone.autoinclude.plugin and a module name."
                    )
                    raise
                logger.exception(
                    f"Could not import {module_name}. Accepted due to "
                    "AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR environment variable."
                )
                _known_module_names[module_name] = None
                continue
            _known_module_names[module_name] = module
        module = _known_module_names[module_name]
        if module is not None:
            dists[module_name] = module
    return dists


def load_own_packages(target=""):
    """Load packages from the plone.autoinclude.plugin entry points.

    After running the function, the packages have been imported.
    This returns a dictionary of package names and packages.

    Etnry points are like this:

        [plone.autoinclude]
        target = plone
        module = collective.mypackage

    Both options are optional, but you must have at least one,
    and it must have a value.
    """
    dists = {}
    for dist_obj in distributions():
        eps = dist_obj.entry_points.select(group="plone.autoinclude.plugin")
        if not eps:
            continue
        module_name = None
        this_target = True
        for ep in eps:
            # If we look for target 'plone' then only consider entry points
            # that are registered for this target (module name).
            # But if the entry point is not registered for a specific target,
            # we can include it.  The biggest reason for doing this,
            # is that I first thought you could not specify both
            # target and module at the same time.
            if ep.name == "target":
                if target and ep.value != target:
                    # entry point defines target X but we only want target Y.
                    this_target = False
                    break
                # We should always be able to get the distribution.
                # Otherwise: how could we have an entry point?
                if module_name is None:
                    module_name = _get_module_name_from_project_name(dist_obj.name)
            if ep.name == "module":
                # We could load the dist with ep.load(), but we do it differently.
                module_name = ep.value
        if not this_target:
            continue
        if module_name is None:  # pragma: no cover
            # We could log a warning, but really this is an error.
            raise ValueError(
                "plone.autoinclude.plugin entry point with no suitable name found."
            )
        if module_name not in _known_module_names:
            # We could try/except ModuleNotFoundError, but this is an unexpected error.
            module = importlib.import_module(module_name)
            _known_module_names[module_name] = module
        else:
            module = _known_module_names[module_name]
        dists[module_name] = module
    return dists


def load_packages(target=""):
    """Load packages from the autoinclude entry points.

    After running the function, the packages have been imported.
    This returns a dictionary of package names and packages.
    """
    dists = load_own_packages(target=target)
    z3c_dists = load_z3c_packages(target=target)
    dists.update(z3c_dists)
    return dists


def get_zcml_file(module_name, zcml="configure.zcml"):
    try:
        filename = str(files(module_name) / zcml)
    except ModuleNotFoundError:
        # Note: this may happen a lot, at least for z3c.autoinclude,
        # because the project name may not be the same as the package/module.
        logger.exception(f"Could not import {module_name}.")
        _known_module_names[module_name] = None
        return
    if not os.path.isfile(filename):
        return
    return filename


def load_zcml_file(
    context, module_name, package=None, zcml="configure.zcml", override=False
):
    filename = get_zcml_file(module_name, zcml)
    if not filename:
        return
    if package is None and context.package is not None:
        package = context.package
    if override:
        logger.debug(f"Loading {module_name}:{zcml} from {filename} in override mode.")
        # The package as third argument seems not needed because we have an absolute file name.
        # But it *is* needed when that file loads other relative files.
        includeOverrides(context, filename, package)
    else:
        logger.debug(f"Loading {module_name}:{zcml} from {filename}")
        include(context, filename, package)


def load_configure(context, filename, dists):
    logger.debug(f"Loading {filename} files.")
    for module_name, package in dists.items():
        logger.debug(module_name)
        load_zcml_file(context, module_name, package, filename)


def load_overrides(context, filename, dists):
    logger.debug(f"Loading {filename} files in override mode.")
    for module_name, package in dists.items():
        logger.debug(module_name)
        load_zcml_file(context, module_name, package, "overrides.zcml", override=True)
