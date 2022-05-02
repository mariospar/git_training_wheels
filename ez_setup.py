#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Bootstrap setuptools installation.

To use setuptools in your package's setup.py, include this
file in the same directory and add this to the top of your setup.py::

    from ez_setup import use_setuptools
    use_setuptools()

To require a specific version of setuptools, set a download
mirror, or use an alternate download directory, simply supply
the appropriate options to ``use_setuptools()``.

This file can also be run as a script to install or upgrade setuptools.
"""

# Credits to https://github.com/embray/setup.cfg/blob/master/ez_setup.py

from __future__ import annotations

import contextlib
import optparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import textwrap
import zipfile
from collections.abc import Callable, Sequence
from distutils import log
from types import TracebackType
from typing import Any, Optional

try:

    from urllib.request import urlopen

except ImportError:

    from urllib2 import urlopen  # type: ignore[no-redef]


try:

    from site import USER_SITE

except ImportError:

    USER_SITE = None


DEFAULT_VERSION = "62.1.0"
DEFAULT_URL = "https://pypi.python.org/packages/source/s/setuptools/"


def _python_cmd(*args: Any) -> bool:
    """Return True if the command succeeded."""
    args = (sys.executable,) + args

    return subprocess.call(args) == 0


def _install(archive_filename: str, install_args: Sequence[str] = ()) -> int:

    with archive_context(archive_filename):

        # installing
        log.warn("Installing Setuptools")

        if not _python_cmd("setup.py", "install", *install_args):

            log.warn("Something went wrong during the installation.")

            log.warn("See the error message above.")
            # exitcode will be 2

            return 2
    return 0


def _build_egg(egg: str, archive_filename: str, to_dir: str) -> None:

    with archive_context(archive_filename):

        # building an egg

        log.warn("Building a Setuptools egg in %s", to_dir)

        _python_cmd("setup.py", "-q", "bdist_egg", "--dist-dir", to_dir)

    # returning the result
    log.warn(egg)

    if not os.path.exists(egg):

        raise IOError("Could not build the egg.")


class ContextualZipFile(zipfile.ZipFile):
    """Supplement ZipFile class to support context manager for Python 2.6."""

    def __enter__(self) -> Any:
        """Open file."""
        return self

    def __exit__(
        self,
        type: Optional[type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Close file."""
        self.close()

    def __new__(cls: type[ContextualZipFile], *args: Any, **kwargs: Any) -> Any:
        """Construct a ZipFile or ContextualZipFile as appropriate."""
        if hasattr(zipfile.ZipFile, "__exit__"):

            return zipfile.ZipFile(*args, **kwargs)

        return super(ContextualZipFile, cls).__new__(cls)


@contextlib.contextmanager
def archive_context(filename: str) -> Any:
    """Extract the archive.

    Args:
        filename (str): the full path of the file

    Returns:
        Any: The content of the archive
    """
    tmpdir = tempfile.mkdtemp()

    log.warn("Extracting in %s", tmpdir)

    old_wd = os.getcwd()

    try:
        os.chdir(tmpdir)

        with ContextualZipFile(filename) as archive:

            archive.extractall()

        # going in the directory

        subdir = os.path.join(tmpdir, os.listdir(tmpdir)[0])

        os.chdir(subdir)

        log.warn("Now working in %s", subdir)

        yield

    finally:
        os.chdir(old_wd)
        shutil.rmtree(tmpdir)


def _do_download(version: str, download_base: str, to_dir: str, download_delay: int) -> None:
    """Download the package setuptools.

    Args:
        version (str): the version of setuptools
        download_base (str): the url to download the package
        to_dir (str): the directory to download it
        download_delay (int): Seconds to wait for download
    """
    egg = os.path.join(
        to_dir, "setuptools-%s-py%d.%d.egg" % (version, sys.version_info[0], sys.version_info[1])
    )

    if not os.path.exists(egg):

        archive = download_setuptools(version, download_base, to_dir, download_delay)

        _build_egg(egg, archive, to_dir)

    sys.path.insert(0, egg)

    # Remove previously-imported pkg_resources if present (see
    # https://bitbucket.org/pypa/setuptools/pull-request/7/ for details).

    if "pkg_resources" in sys.modules:

        del sys.modules["pkg_resources"]

    import setuptools

    setuptools.bootstrap_install_from = egg


def use_setuptools(
    version: str = DEFAULT_VERSION,
    download_base: str = DEFAULT_URL,
    to_dir: str = os.curdir,
    download_delay: int = 15,
) -> Any:
    """Resolve conflicts with pkg_resources module.

    Args:
        version (str, optional): The version of setuptools. Defaults to DEFAULT_VERSION.
        download_base (str, optional): The URL to download it from. Defaults to DEFAULT_URL.
        to_dir (str, optional): The directory to download it to. Defaults to os.curdir.
        download_delay (int, optional): The delay to wait for download. Defaults to 15.

    Returns:
        Any: Calls the _do_download function which executes the download
    """
    to_dir = os.path.abspath(to_dir)

    rep_modules = "pkg_resources", "setuptools"

    imported = set(sys.modules).intersection(rep_modules)

    try:

        import pkg_resources  # type: ignore[import]

    except ImportError:

        return _do_download(version, download_base, to_dir, download_delay)

    try:

        pkg_resources.require(f"setuptools>={version}")
        return

    except pkg_resources.DistributionNotFound:

        return _do_download(version, download_base, to_dir, download_delay)

    except pkg_resources.VersionConflict as VC_err:

        if imported:

            msg = textwrap.dedent(
                """\x1f                The required version of setuptools (>={version}) is not available,\x1f                and can't be installed while this script is running. Please\x1f                install a more recent version first, using\x1f                'easy_install -U setuptools'.\x1f\x1f                (Currently using {VC_err.args[0]!r})\x1f                """
            ).format(VC_err=VC_err, version=version)

            sys.stderr.write(msg)

            sys.exit(2)

        del pkg_resources, sys.modules["pkg_resources"]

        return _do_download(version, download_base, to_dir, download_delay)


def _clean_check(cmd: list[str], target: str) -> None:
    """Run the command to download target. If the command fails, clean up before re-raising the error."""
    try:

        subprocess.check_call(cmd)

    except subprocess.CalledProcessError:

        if os.access(target, os.F_OK):

            os.unlink(target)
        raise


def download_file_powershell(url: str, target: str) -> None:
    """Download the file at url to target using Powershell (which will validate trust).

    Raise an exception if the command cannot complete.
    """
    target = os.path.abspath(target)

    ps_cmd = (
        "[System.Net.WebRequest]::DefaultWebProxy.Credentials = "
        "[System.Net.CredentialCache]::DefaultCredentials; "
        "(new-object System.Net.WebClient).DownloadFile(%(url)r, %(target)r)" % vars()
    )

    cmd = [
        "powershell",
        "-Command",
        ps_cmd,
    ]

    _clean_check(cmd, target)


def has_powershell() -> bool:
    """Check if computer has powershell installed.

    Returns:
        bool: has powershell?
    """
    if platform.system() != "Windows":

        return False

    cmd = ["powershell", "-Command", "echo test"]

    with open(os.path.devnull, "wb") as devnull:

        try:

            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)

        except Exception:

            return False

    return True


setattr(download_file_powershell, "viable", has_powershell)


def download_file_curl(url: str, target: str) -> None:
    """Download the file at url to target using cURL (which will validate trust)."""
    cmd = ["curl", url, "--silent", "--output", target]

    _clean_check(cmd, target)


def has_curl() -> bool:
    """Check if computer has cURL installed.

    Returns:
        bool: has cURL?
    """
    cmd = ["curl", "--version"]

    with open(os.path.devnull, "wb") as devnull:

        try:

            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)

        except Exception:

            return False

    return True


setattr(download_file_curl, "viable", has_curl)


def download_file_wget(url: str, target: str) -> None:
    """Download the file at url to target using wget (which will validate trust)."""
    cmd = ["wget", url, "--quiet", "--output-document", target]

    _clean_check(cmd, target)


def has_wget() -> bool:
    """Check if computer has wget installed.

    Returns:
        bool: has wget?
    """
    cmd = ["wget", "--version"]

    with open(os.path.devnull, "wb") as devnull:

        try:

            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)

        except Exception:

            return False

    return True


setattr(download_file_wget, "viable", has_wget)


def download_file_insecure(url: str, target: str) -> None:
    """Use Python to download the file, even though it cannot authenticate the connection."""
    src = urlopen(url)

    try:

        # Read all the data in one block.

        data = src.read()

    finally:
        src.close()

    # Write all the data in one block to avoid creating a partial file.

    with open(target, "wb") as dst:
        dst.write(data)


setattr(download_file_insecure, "viable", lambda: True)


def get_best_downloader() -> Any:
    """Configure the optimal downloader.

    Returns:
        Any: A callable optimal downloader
    """
    downloaders: tuple[Callable[[str, str], None], ...] = (
        download_file_powershell,
        download_file_curl,
        download_file_wget,
        download_file_insecure,
    )

    viable_downloaders = (dl for dl in downloaders if dl.viable())  # type: ignore[attr-defined]

    return next(viable_downloaders, None)


def download_setuptools(
    version: str = DEFAULT_VERSION,
    download_base: str = DEFAULT_URL,
    to_dir: str = os.curdir,
    delay: int = 15,
    downloader_factory: Any = get_best_downloader,
) -> str:
    """Download setuptools from a specified location and return its filename.

    `version` should be a valid setuptools version number that is available
    as an egg for download under the `download_base` URL (which should end
    with a '/'). `to_dir` is the directory where the egg will be downloaded.
    `delay` is the number of seconds to pause before an actual download
    attempt.

    ``downloader_factory`` should be a function taking no arguments and
    returning a function for downloading a URL to a target.
    """
    to_dir = os.path.abspath(to_dir)  # making sure we use the absolute path

    zip_name = f"setuptools-{version}.zip"

    url = download_base + zip_name
    svt = os.path.join(to_dir, zip_name)

    if not os.path.exists(svt):  # Avoid repeated downloads

        log.warn("Downloading %s", url)

        downloader = downloader_factory()
        downloader(url, svt)
    return os.path.realpath(svt)


def _build_install_args(options: Any) -> Sequence[str]:
    """Build the arguments to 'python setup.py install' on the setuptools package."""
    return ("--user") if options.user_install else ()


def _parse_args() -> Any:
    """Parse the command line for options."""
    parser = optparse.OptionParser()
    parser.add_option(
        "--user",
        dest="user_install",
        action="store_true",
        default=False,
        help="install in user site package (requires Python 2.6 or later)",
    )
    parser.add_option(
        "--download-base",
        dest="download_base",
        metavar="URL",
        default=DEFAULT_URL,
        help="alternative URL from where to download the setuptools package",
    )
    parser.add_option(
        "--insecure",
        dest="downloader_factory",
        action="store_const",
        const=lambda: download_file_insecure,
        default=get_best_downloader,
        help="Use internal, non-validating downloader",
    )
    parser.add_option(
        "--version",
        help="Specify which version to download",
        default=DEFAULT_VERSION,
    )

    options, args = parser.parse_args()

    # positional arguments are ignored
    return options


def main() -> int:
    """Install or upgrade setuptools."""
    options = _parse_args()

    archive = download_setuptools(
        version=options.version,
        download_base=options.download_base,
        downloader_factory=options.downloader_factory,
    )

    return _install(archive, _build_install_args(options))


if __name__ == "__main__":

    sys.exit(main())
