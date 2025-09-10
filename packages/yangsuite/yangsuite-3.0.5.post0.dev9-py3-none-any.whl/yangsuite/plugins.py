# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

from django.apps import apps
from django.core.management import execute_from_command_line
import json
import os
import importlib
from packaging.version import Version, InvalidVersion
from pkg_resources import iter_entry_points, VersionConflict
import re
import subprocess
import sys
import requests
from bs4 import BeautifulSoup as soup
from django.conf import settings
from dataclasses import dataclass
from typing import List
from yangsuite.logs import get_logger
from yangsuite.apps import FAILED_APPS
from ysdevices.devprofile import YSDeviceProfile
from http.client import responses
from pathlib import Path

log = get_logger(__name__)

VERSIONS_REGEX = re.compile(r"(\d+)")

ALL_PUBLICS_APPS = [
    # New names of application for Yangsuite
    # shared on pypi should be add here
    "yangsuite",
    "yangsuite-restconf",
    "yangsuite-devices",
    "yangsuite-netconf",
    "yangsuite-coverage",
    "yangsuite-yangtree",
    "yangsuite-filemanager",
    "yangsuite-gnmi",
    "yangsuite-grpc-telemetry",
]

INTERNAL_APPS = [
    'yangsuite-testmanager',
    'yangsuite-framq'
]

EXCLUDED_APPS = [
    "yangsuite-app-template",
    "yangsuite-mapper",
    "yangsuite-impact",
    "yangsuite-ydk",
    "yangsuite-IBCR",
    "yangsuite-doc-builder",
    "yangsuite-mapper-xrcodegen",
    "yangsuite-mapper-erlang",
    "yangsuite-pipeline",
]

SNAPSHOTS_DIR = Path(settings.MEDIA_ROOT) / "plugins_snapshots"


@dataclass
class Plugin:
    """Data class for plugin version information."""
    package_name: str
    description: str
    installed_version: str = ''
    module_name: str = ''
    error_message: str = ''
    latest_version: str = ''

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Plugin):
            return self.package_name == __value.package_name
        return self.package_name == __value


def inform(message):
    """Pretty-print a message to the user."""
    print("*" * 70)
    print(message)
    print("*" * 70)


def create_plugin_list(releases: list) -> Plugin:
    revs = sorted(
        releases,
        key=(
            lambda x: [
                int(VERSIONS_REGEX.search(v).group(1)) for v in x.split(".")
            ]
        ),
        reverse=True,
    )
    if "dev" in revs[0]:
        latest = next((ver for ver in revs if "dev" not in ver), None)
    else:
        latest = revs[0]
    return latest


def get_installed_plugins():
    """Get the installed YANG Suite plugins and their versions.

    Returns:
      list: of dicts with keys 'package_name', 'installed_version',
        'module_name', 'verbose_name', 'error_message'
    """
    plugins: List[Plugin] = []
    # For each installed plugin, we have a pkg_resources entry_point which
    # lets us look up a Django YSAppConfig.
    #
    # entry_point:                       pkg_resources.EntryPoint
    #   name = 'yangtree'
    #   module_name = 'ysyangtree.apps'
    #   attrs = ('YSYangTreeConfig', )
    #   extras = ()
    #   dist:                            pkg_resources.DistInfoDistribution
    #     project_name = 'yangsuite-yangtree'
    #     version = '0.4.1'
    #     key = 'yangsuite-yangtree'     (project_name.lower())
    #
    # app_config:                        YSAppConfig
    #   name: 'ysyangtree'               full python module path
    #   label: 'ysyangtree'              last part of name, overridable
    #   verbose_name: 'YANG Tree app'    defaults to label.upper() if unset
    #
    # TODO: we should also be able to use the 'pkginfo' module to read
    # additional package info, such as Summary and Description,
    # but this appears non-trivial.
    for entry_point in iter_entry_points(group="yangsuite.apps", name=None):
        dist = entry_point.dist
        plugin = Plugin(
            dist.project_name, "(unknown)", dist.version, "(unknown)"
        )
        if dist.project_name in FAILED_APPS:
            plugin.error_message = FAILED_APPS[dist.project_name]
        else:
            try:
                ac_class = entry_point.load()
                app_config = apps.get_app_config(ac_class.name)
                plugin.module_name = app_config.name
                plugin.description = app_config.verbose_name
            except VersionConflict as exc:
                plugin.error_message = exc.report()
            except Exception as exc:
                plugin.error_message = str(exc)
        plugins.append(plugin)
    installed_plugins = sorted(plugins, key=lambda x: x.package_name)
    log.info("Installed plugins: %s", [x.package_name for x in installed_plugins])

    return installed_plugins


def call_pip(args):
    """Invoke pip with the given list of
    args and return output as a string."""
    try:
        output = subprocess.check_output(["pip"] + args, stderr=None)
        # On python 3, depending on user locale, subprocess.check_output
        # may return either a str or bytes. Handle it either way
        if not isinstance(output, str):
            output = output.decode()
        return output
    except subprocess.CalledProcessError as exc:
        # May occur if pypi server is unreachable, etc.
        inform("pypi server is unreachable")
        log.error(
            '"pip %s" failed with exit code %d', " ".join(args), exc.returncode
        )
        log.debug("pip output:\n%s", exc.output)
        return ""


def tag_sort(x):
    xs = x.split(".")
    if xs and len(xs) > 1:
        if xs[0].replace("v", "") == "0":
            return 0
        return int(xs[1])
    return int(1)


def get_public_packages() -> List[Plugin]:
    """
    Check the latest versions of YANG Suite and Yang Suite plugins on pypi.org.
    Check for all available and installed apps.

    Returns:
      List[PluginVersions]: List of objects with information about latest versions
    """

    # Used for prepare data for Admin -> Manage plugins
    # Returns collective list, Division into categories:
    # "Core YANG Suite plugins" , "Installed optional plugins",
    # "Additional plugins not currently installed"
    # is being handled on front-end

    plugins = []
    installed_apps = iter_entry_points(group="yangsuite.apps", name=None)
    installed_apps_names = map(lambda x: x.dist.project_name, installed_apps)
    all_apps_names = filter(
        lambda x: x not in EXCLUDED_APPS,
        set().union(ALL_PUBLICS_APPS, installed_apps_names),
    )

    for app_name in all_apps_names:
        resp = requests.get(f"https://pypi.org/pypi/{app_name}/json")
        if resp.status_code == 200:
            data = resp.json()
            latest_version = create_plugin_list(data["releases"].keys())
            plugins.append(Plugin(app_name,
                                  data["info"]["summary"],
                                  latest_version=latest_version))
        else:
            plugins.append(
                Plugin(
                    app_name,
                    "Something went wrong. Request status to "
                    + f"pypi.org: {resp.status_code} - '{responses[resp.status_code]}'",
                )
            )

    return plugins


def get_all_available_plugins() -> List[Plugin]:
    """Check upstream repository for available YANG Suite plugins.

    Since this involves network operations it can be somewhat slow, which
    is why this is a separate function from :func:`get_plugin_versions`.

    Returns:
      List[PluginVersions]: List of objects with information about latest versions
    """
    plugins = []
    try:
        smod = importlib.import_module(
            os.getenv(
                "DJANGO_SETTINGS_MODULE", "yangsuite.settings.production"
            )
        )
    except ImportError:
        log.error("Unable to find Django settings: CISCO_PYPI")
        return plugins
    if not hasattr(smod, "CISCO_PYPI"):
        return get_public_packages()
    installed_apps = iter_entry_points(group="yangsuite.apps", name=None)
    installed_apps_names = map(lambda x: x.dist.project_name, installed_apps)

    # Find out all internal apps by querying CISCO_PYPI
    resp = requests.get(smod.CISCO_PYPI)
    if resp.ok:
        bxml = soup(resp.content, 'html.parser')
        wheels = [w.text for w in bxml.find_all('a')]
        all_internal_apps = [w.text for w in bxml.find_all('a')
                             if w.text.startswith('yangsuite')]
    else:
        all_internal_apps = []

    all_apps_names = filter(
        lambda x: x not in EXCLUDED_APPS,
        set().union(all_internal_apps, installed_apps_names),
    )
    try:
        for app in all_apps_names:
            resp = requests.get(smod.CISCO_PYPI+app+'/')
            if resp.ok:
                bxml = soup(resp.content, 'html.parser')
                wheels = [w.text for w in bxml.find_all('a')]

                rel = 'Unknown'
                rel_list = []
                img = wheels.pop()
                while img:
                    img = img.replace('yangsuite', '').replace('_', '')
                    if '.post' in img:
                        rel = img[img.find('-')+1:img.find('.post')]
                    else:
                        rel = img.split('-')[1]
                    rel_list.append(rel)
                    img = ''
                    if wheels:
                        img = wheels.pop()

                rel_names = sorted(
                    rel_list,
                    key=(
                        lambda x: [
                            int(v) if v.isdigit() else 0 for v in x.split(".")
                        ]
                    ),
                    reverse=True
                )
                # TODO Latest version info return
                if len(rel_names) > 0:
                    plugins.append(Plugin(app, app))
        plugins = sorted(plugins, key=lambda x: x.package_name)
        log.info(
            "Available plugins: %s", [x["package_name"] for x in plugins]
        )
        return plugins

    except Exception as e:
        log.error("Unable to collect repository infomation {0}".str(e))
    finally:
        return plugins


def load_snapshot(snapshot_name: str):
    snapshot_path = Path(settings.SNAPSHOTS_DIR) / str(snapshot_name)
    if not snapshot_path.exists():
        return False
    args = [
        "install",
        "-r",
        str(snapshot_path)
    ]
    output = call_pip(args)
    if not output or re.search("ERROR", output):
        return False
    return True


def update_ys_database():
    """Migrate changes to database if needed for plugin updates."""
    try:
        for entry_point in iter_entry_points(
            group="yangsuite.apps", name=None
        ):
            try:
                app = entry_point.load()
                execute_from_command_line(
                    ["manage", "makemigrations", app.name, "--no-color"]
                )
            except Exception:
                continue
        execute_from_command_line(["manage", "migrate", "--no-color"])
    except Exception as exc:
        log.error("Database migrations failed: {0}".format(str(exc)))


def update_plugins(plugins_to_install: list = None, install_pre_release: bool = False):
    """Update the given plugin to the latest release or pre-release version.

    Args:
      pre_release_plugins (list): List of package names to install pre-release.
      If empty, install latest release version.

    Returns:
      dict: Package names as keys, each value is one of "updated",
      "unchanged", or "failed"
    """
    # Let pip pick correct latest version
    # plugins = check_for_plugin_updates()
    args = [
        "install",
        "--upgrade",
        "--extra-index-url",
        "https://engci-maven.cisco.com/artifactory/"
        "api/pypi/yang-suite-dev-pypi/simple",
    ]
    if install_pre_release:
        args.append("--pre")

    try:
        smod = importlib.import_module(
            os.getenv(
                "DJANGO_SETTINGS_MODULE", "yangsuite.settings.production"
            )
        )
    except ImportError:
        smod = {}

    if plugins_to_install:
        # Used by pre-release installation
        plugins = plugins_to_install
    else:
        # Update all installed plugins to latest
        installed_apps = iter_entry_points(group="yangsuite.apps", name=None)
        installed_apps_names = map(lambda x: x.dist.project_name, installed_apps)
        plugins = filter(lambda x: x not in EXCLUDED_APPS, installed_apps_names)
        if not hasattr(smod, "CISCO_PYPI"):
            # For public we update only public apps
            plugins = list(set(installed_apps_names).intersection(ALL_PUBLICS_APPS))
        else:
            plugins = list(plugins)
        plugins = [
            f"{plugin.package_name}=={plugin.latest_version}"
            for plugin in get_all_available_plugins()
            if plugin in plugins
        ]

    ret = {"plugins": {}}
    result = {}
    any_updated = False
    special_reboot = False
    docker_run = os.environ.get("DOCKER_RUN", False)
    args.extend(plugins)

    try:
        output = call_pip(args)
        for plugin in plugins:
            if not output:
                result[plugin] = "failed"
            elif re.search(
                f"Successfully installed .*{plugin}", output
            ):
                result[plugin] = "updated"
                any_updated = True
            else:
                result[plugin] = "unchanged"
    finally:
        # Re-enable autoreloading, if applicable
        # if user does not want to restart yangsuite server
        # after each plugin installation then disable if
        # condition - only used in docker container
        if docker_run or docker_run == "true":
            pid_file = settings.BASE_DIR + "/ys-master.pid"
            os.system("uwsgi --reload {0}".format(pid_file))
        special_reboot = True

    if any_updated:
        # cause the Django server to self-restart, picking up the new code.
        update_ys_database()
    ret["plugins"] = result
    ret["success"] = True
    if any(status == "updated" for status in result.values()):
        # What mode are we running in?
        if special_reboot:
            ret["message"] = "This update requires yangsuite server reboot."
        elif docker_run == "true" or os.environ.get("RUN_MAIN") == "true":
            ret["message"] = "YANG Suite server will automatically restart."
        else:
            ret["message"] = (
                "You will need to refresh the browser "
                "for these changes to take effect."
            )
    elif all(status == "unchanged" for status in result.values()):
        ret["message"] = "Everything is up to date."
    else:
        ret["message"] = "Check YANG Suite logs for details."
    if any(status == "failed" for status in result.values()):
        ret["success"] = False
    ret['any_updated'] = any_updated
    return ret


def _version_list_from_pip_command(extra_args=None):
    """Calls 'pip list --format=json [extra_args]' and parses the output.

    Helper for :func:`python_report`.

    The above command gives us a list of dicts, of form
    ``[{'name': 'foo', 'version': "0.1.2"}, ..]`` or
    ``[{'name': 'bar', 'version': "0.1.2", 'latest_version': "1.2.0"}, ...]``

    Args:
      extra_args (list): List of additional args to pass to the base
        'pip list --format=json' command

    Returns:
      dict: {name: latest_version, name: latest_version, ...},
        or None in case of error.
    """
    args = ["list", "--format=json"]
    if extra_args:
        args += extra_args
    try:
        # Check if there's a newer release version than what we have
        output = call_pip(args)
        if not output:
            return None

        # Even though we redirect stderr above, pip has a bad habit of
        # printing error messages to stderr which result in malformed "JSON",
        # such as:
        # Could not fetch URL https://<...> There was a problem...
        #
        # As a rough attempt at a workaround, we'll drop lines until we get to
        # a line that looks like it could be JSON.
        pkgs_lines = []
        for line in output.splitlines():
            if not line.startswith("[{"):
                continue
            pkgs_lines.append(line)
        pkgs_json = "\n".join(pkgs_lines)
        pkgs_list = json.loads(pkgs_json)
    except ValueError:
        log.error("Unable to decode message as JSON")
        log.debug("pip output:\n%s", pkgs_json)
        return None

    # The above command gives us a list of dicts, of form
    # [{'name': 'foo', 'version': "0.1.2"},]
    # Let's change it around to something a bit more useful for our needs.
    result = {}
    for entry in pkgs_list:
        # Get 'latest_version' if available, else 'version'
        vers = entry.get("latest_version", entry["version"])
        try:
            version = Version(vers)
        except InvalidVersion as e:
            # PEP-440-compliant version
            log.error(
                "Invalid version '%s' for package '%s': %s",
                vers,
                entry["name"],
                e,
            )
            version = str(e)
        result[entry["name"]] = version

    return result


def python_report():
    """Report on the overall Python system status.

    Returns:
      dict: {python: {version: "3.6.5 ..."}, modules: [...]}
    """
    installed_pkgs = _version_list_from_pip_command()
    for name in installed_pkgs.keys():
        installed_pkgs[name] = str(installed_pkgs[name])
    return {
        "python": {"version": str(sys.version)},
        "modules": installed_pkgs,
    }


def _verify_callback(data):
    if data:
        ln = [
            ln
            for ln in data.splitlines()
            if ln.strip().startswith("dna-advantage")
        ]
        if ln:
            line = ln[0].split()
            if line[len(line) - 1] == "EXPIRED":
                return False
            else:
                return True
    return False


def _check_available(
    dev, cmd="show license summary", callback=_verify_callback
):
    """Check availability of a device."""
    if isinstance(dev, YSDeviceProfile):
        dev_profile = dev
    else:
        dev_profile = YSDeviceProfile.get(dev)
    try:
        dev_profile.ssh.connect()
        return callback(dev_profile.ssh.send_exec(cmd))
    except Exception:
        print("Check class failed: {0}".format((str(Exception))))
        return False
