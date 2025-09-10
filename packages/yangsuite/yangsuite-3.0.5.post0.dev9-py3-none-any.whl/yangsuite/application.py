#! /usr/bin/env python
# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

"""Start the YANG Suite server."""

import os
import configparser
import django
import socket
import sys
import webbrowser
import subprocess
import shutil
from pathlib import Path
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime, timedelta
from ipaddress import ip_address
from pkg_resources import iter_entry_points
from appdirs import AppDirs
from django.core.management import execute_from_command_line
from django.core.management.utils import get_random_secret_key
from django.conf import settings
from django.contrib.auth import get_user_model
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.exceptions import InvalidSignature
from yangsuite.common import create_packages_snapshot

DEFAULT_ALLOWED_HOSTS = 'localhost 127.0.0.1'
yangsuite_dirs = AppDirs('yangsuite')
config_file_path = os.path.dirname(os.path.realpath(__file__))

yangsuite_prefs = os.path.join(yangsuite_dirs.user_config_dir, 'yangsuite.ini')
YANG_CERT_STORE = os.path.join(yangsuite_dirs.user_data_dir, 'cert_store')
YANG_PKEY_PATH = os.path.join(YANG_CERT_STORE, 'yang_key.pem')
YANG_CERT_PATH = os.path.join(YANG_CERT_STORE, 'yang_cert.pem')

# Preferences and their suggested defaults if any
DEFAULT_PREFERENCES = {
    'data_path': '',
    'port': '8480',
    'secret_key': get_random_secret_key(),
    'static_root': os.path.join(yangsuite_dirs.user_data_dir, 'static'),
    'allowed_hosts': DEFAULT_ALLOWED_HOSTS,
    'certificate_path': '/path/to/certificate/file.pem',
    'private_key_path': '/path/to/private_key/file.pem',
    # Default to development mode because deployment to production
    # is non-trivial to implement.
    'settings_module': 'yangsuite.settings.dev.develop',

    # User must accept Cisco General Terms
    'eula_agreement': 'declined',

    # Cisco DNA advantage
    'dna_advantage': 'detect'
}
# /Users/miott/Library/Application\ Support/yangsuite/yangsuite.ini


def read_prefs():
    """Load the preferences file, if any, into a ConfigParser object."""
    global yangsuite_prefs
    config = configparser.ConfigParser(defaults=DEFAULT_PREFERENCES,
                                       interpolation=None)
    config_file = os.path.join(config_file_path, 'yangsuite.ini')
    if os.path.exists(yangsuite_prefs):
        config.read(yangsuite_prefs)
    elif os.path.exists(config_file):
        config.read(config_file)
        yangsuite_prefs = config_file
    return config


def write_prefs(config):
    """Write the given ConfigParser object to the preferences file."""
    config_file = os.path.join(config_file_path, 'yangsuite.ini')
    if not os.path.isdir(yangsuite_dirs.user_config_dir):
        with open(config_file, 'w') as fd:
            config.write(fd)
        inform("{0} directory doesn't exist. Saving configuration "
               "file to {1}"
               .format(yangsuite_dirs.user_config_dir, config_file))
    else:
        try:
            with open(yangsuite_prefs, 'w') as fd:
                config.write(fd)
        except OSError:
            # EnXR environment has restricted directory access and
            # permission resulting in OSError when writing to
            # /users directory. So save config file to a different path
            with open(config_file, 'w') as fd:
                config.write(fd)


def find_settings_spec(prefs, config, production, develop):
    settings_mod = prefs.get('settings_module') or develop

    # Find the settings module first
    develop_settings_path = os.path.join(
        os.path.dirname(__file__),
        'settings/dev/develop.py')

    if settings_mod in [
        'yangsuite.settings.develop',
        'yangsuite.settings.dev.develop'
    ] and os.path.exists(develop_settings_path):
        settings_mod = develop
    else:
        settings_mod = production

    # Change settings
    if prefs['settings_module'] != settings_mod:
        prefs['settings_module'] = settings_mod
        if not prefs['allowed_hosts']:
            # production requires a setting here so set default localhost
            prefs['allowed_hosts'] = DEFAULT_ALLOWED_HOSTS
        write_prefs(config)


def main():
    """Main execution entry point for configuring YANG Suite."""
    production = 'yangsuite.settings.production'
    develop = 'yangsuite.settings.dev.develop'
    config = read_prefs()
    prefs = config[configparser.DEFAULTSECT]

    if prefs['settings_module'] != production:
        # New: develop settings may have been removed from package
        find_settings_spec(prefs, config, production, develop)

    parser = ArgumentParser(description="YANG Suite server",
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('-l', '--list', action='store_true',
                        help="List YANG Suite server settings.")
    parser.add_argument('--save-settings', action='store_true',
                        help="Save provided options as YANG Suite defaults "
                        "in file %s" % yangsuite_prefs)
    parser.add_argument('-i', '--interactive', action='store_true',
                        help="Force interactive entry of config options"
                        " even if config file exists")
    parser.add_argument('-c', '--configure-only', action='store_true',
                        help="Configure but do not launch YANG Suite server.")

    basic_group = parser.add_argument_group('Basic server options')
    basic_group.add_argument(
        '-d', '--data-path',
        default=prefs.get('data_path'),
        help="Directory path where YANG Suite data is to be saved, including "
        "YANG module files, user accounts, device profiles, etc. "
        "Make sure you regularly back up this directory.")
    basic_group.add_argument(
        '-p', '--port', type=int,
        default=prefs.getint('port'),
        help="Port number to listen on")
    basic_group.add_argument(
        '-a', '--allowed-hosts', nargs='+', metavar='HOST',
        default=prefs.get('allowed_hosts').split(),
        help="IP address(s) and/or hostname(s) that YANG Suite can be "
        "accessed by. Leave blank for local access only. "
        "Use '*' to allow all addresses of this system")

    advanced_group = parser.add_argument_group('Advanced server options')
    advanced_group.add_argument(
        '-m', '--settings-module',
        default=prefs.get('settings_module'),
        help="Python module containing YANG Suite settings")
    advanced_group.add_argument(
        '-k', '--key', '--secret-key',
        default="(not shown)",
        help="Secret key used for cryptographic signing")
    advanced_group.add_argument(
        '--create-admin-user', action='store_true',
        help="Create a YANG Suite admin superuser (interactive only)")
    advanced_group.add_argument(
        '-s', '--static-root', default=prefs.get('static_root'),
        help="Directory where static files should be stored "
        "when running with production settings file.")
    advanced_group.add_argument(
        '--debug', action='store_true',
        help="Runs Django using development web server.")

    https_group = parser.add_argument_group('HTTPS server options')
    https_group.add_argument(
        '--https', action='store_true',
        help="Run yangsuite with HTTPS (ssl encryption)"
    )

    args = parser.parse_args()

    if args.list:
        items = ''
        for k, v in config.defaults().items():
            if k != 'secret_key':
                items += '{0} - {1}\n'.format(k, v)
        inform("YANG Suite preferences file\n" + 27 * '*' + '\n({0})\n\n'
               "Settings\n********\n{1}"
               .format(yangsuite_prefs, items))
        return

    args.key = (args.key if args.key != "(not shown)"
                else prefs.get('secret_key'))

    args.static_root = os.path.abspath(args.static_root)

    # If required settings are neither present in config nor provided by
    # the user, go into interactive configuration mode.
    if args.interactive or not (args.data_path and
                                args.port):
        configure_interactively(args)

    if args.save_settings:
        inform("Updating YANG Suite preferences file ({0})"
               .format(yangsuite_prefs))
        prefs['data_path'] = args.data_path
        prefs['port'] = str(args.port)
        prefs['allowed_hosts'] = ' '.join(args.allowed_hosts)
        prefs['settings_module'] = args.settings_module
        prefs['secret_key'] = args.key
        prefs['static_root'] = args.static_root
        write_prefs(config)

    if not os.path.isdir(args.data_path):
        # Data path deleted?
        inform("Cannot find data path {0}".format(args.data_path))
        args.data_path = prefs['data_path'] = configure_data_path(
            args.data_path)
        inform("Updating YANG Suite preferences file ({0})"
               .format(yangsuite_prefs))
        write_prefs(config)

    # Set Django to point to YANG Suite settings file
    if args.settings_module == 'yangsuite.settings.develop':
        # Moved development settings to different package
        os.environ['DJANGO_SETTINGS_MODULE'] = 'yangsuite.settings.dev.develop'
    else:
        os.environ['DJANGO_SETTINGS_MODULE'] = args.settings_module
    # Set Django to point to YANG Suite data directory
    os.environ['MEDIA_ROOT'] = args.data_path
    # Specify secret encryption key
    os.environ['DJANGO_SECRET_KEY'] = args.key
    # Specify Django allowed hosts as whitespace-separated string
    os.environ['DJANGO_ALLOWED_HOSTS'] = ' '.join(args.allowed_hosts)
    # Specify static file storage path, and create it if needed
    os.environ['DJANGO_STATIC_ROOT'] = args.static_root

    # Load up Django settings based on the above environment variables
    django.setup()
    from yangsuite.celery_init import app as celery_app # noqa

    # Save installed packages versions to file
    SNAPSHOTS_DIR = Path(settings.SNAPSHOTS_DIR)
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    if os.listdir(SNAPSHOTS_DIR) == []:
        create_packages_snapshot()

    for entry_point in iter_entry_points(
            group='yangsuite.apps', name=None):
        try:
            app = entry_point.load()
            execute_from_command_line(
                ['manage', 'makemigrations', app.name, '--no-color']
            )
        except Exception:
            continue
    execute_from_command_line(['manage', 'migrate', '--no-color'])

    if args.create_admin_user:
        inform("Your input is required to define an admin user")
        execute_from_command_line(['manage', 'createsuperuser'])

    if args.settings_module == 'yangsuite.settings.production':
        # Collect static files to their deployment-ready location
        if not os.path.exists(args.static_root):
            inform("Creating static storage directory {0}"
                   .format(args.static_root))
            os.makedirs(args.static_root)
        execute_from_command_line(['manage', 'collectstatic', '--noinput'])

    if args.configure_only:
        return

    # If we didn't already create a user, we *must* before starting the server
    django_user_model_class = get_user_model()
    if not django_user_model_class.objects.all():
        inform("Your input is required to define an admin user")
        execute_from_command_line(['manage', 'createsuperuser'])

    # Determine how to actually launch the YANG Suite server process
    allowed_hosts = args.allowed_hosts
    port = args.port

    if len(allowed_hosts) == 0:
        addr = "127.0.0.1"
    elif len(settings.ALLOWED_HOSTS) == 1 and settings.ALLOWED_HOSTS[0] != "*":
        addr = settings.ALLOWED_HOSTS[0]
    else:
        addr = "0.0.0.0"

    inform("YANG Suite data is stored at {0}. "
           "Be sure to back up this directory!"
           .format(args.data_path))

    if args.debug:
        sys.exit(execute_from_command_line(['manage',
                                            'runserver',
                                            '--noreload',
                                            '{0}:{1}'.format(addr, port)]))

    if args.https:
        pkey, cert, pkey_path, cert_path = None, None, None, None
        if confirm('Use YANG Suite self-signed certificate (not as secure; y/n)?', 'n'):
            # Using YANG Suite self-signed certificate
            # Create YANG Suite's certificate store if it does not exist
            if not os.path.isdir(YANG_CERT_STORE):
                os.makedirs(YANG_CERT_STORE)

            # Try to load a previous private key
            pkey = load_private_key(YANG_PKEY_PATH)
            if not pkey:
                pkey = create_private_key(YANG_PKEY_PATH)

            # Try to load a previous certificate
            # TODO: maybe also check if addr was updated, to keep certificate as valid as possible
            cert = load_certificate(YANG_CERT_PATH)
            if cert:
                cert = verify_certificate(pkey, cert)
            if not cert:
                cert = create_certificate(YANG_CERT_PATH, pkey, addr)

            # Set path variables for daphne command.
            pkey_path = YANG_PKEY_PATH
            cert_path = YANG_CERT_PATH

        else:
            # Using own certificate
            while not pkey:
                # Get key path
                pkey_path = configure_file_path("Private key path/name", prefs['private_key_path'])
                # Load private key
                pkey = load_private_key(pkey_path)
                if not pkey:
                    inform("Could not find private key file at {0}".format(pkey_path))

            while not cert:
                # Get cert path
                cert_path = configure_file_path("Certificate path/name", prefs['certificate_path'])
                # Load and verify certificate
                cert = load_certificate(cert_path)
                if cert:
                    cert = verify_certificate(pkey, cert)
                if not cert:
                    inform("Could not find x509 certificate file at {0}".format(cert_path))

            # Save given paths for future use
            prefs['private_key_path'] = pkey_path
            prefs['certificate_path'] = cert_path
            inform("Updating YANG Suite preferences file ({0})".format(yangsuite_prefs))
            write_prefs(config)

    # yangsuite server will run using uwsgi server
    # reference: https://docs.djangoproject.com/en/
    # {django-version}/howto/deployment/wsgi/uwsgi/

    # uwsgi ini file variables
    ini_file = settings.BASE_DIR + '/uwsgi.ini'
    # module that startproject creates
    module = 'yangsuite.wsgi:application'
    pidfile = settings.BASE_DIR + '/ys-master.pid'
    virtual_env = sys.prefix + '/'
    section_name = 'uwsgi'
    config_file = configparser.ConfigParser()
    config_file.read(ini_file)

    if not config_file.has_section(section_name):
        config_file.add_section(section_name)
        config_file.set(section_name, "module", module)
        config_file.set(section_name, "master", 'true')
        config_file.set(section_name, "pidfile", pidfile)
        config_file.set(section_name, "home", virtual_env)
        config_file.set(section_name, "harakiri", '3600000')
        config_file.set(section_name, "http-timeout", '3600000')
        config_file.set(section_name, "socket-timeout", '3600000')
        config_file.set(section_name, "honour-stdin", "true")
        config_file.set(section_name, "daemons-honour-stdin", "true")
        with open(ini_file, 'w') as config_ini:
            config_file.write(config_ini)

    # if condition is only used in docker container
    docker_run = os.environ.get('DOCKER_RUN', False)
    if docker_run or docker_run == "true":
        os.system('uwsgi --http={0}:{1} --ini {2} --processes 4 \
        --threads 2'.format(addr, port, ini_file))
    elif args.https:
        os.system('daphne -e ssl:port={0}:interface={1}:privateKey={2}:certKey={3} '
                  'yangsuite.asgi:application'
                  .format(port, addr, pkey_path, cert_path))
    else:
        sys.exit(execute_from_command_line(['manage',
                                            'runserver',
                                            '--noreload',
                                            '{0}:{1}'.format(addr, port)]))


def configure_interactively(args):
    """User will enter configuration from the command prompt."""
    inform("Entering interactive configuration mode")

    args.data_path = configure_data_path(default_value=args.data_path)
    args.port = configure_port(default_value=args.port)
    args.allowed_hosts = configure_access(default_value=args.allowed_hosts)

    # We don't provide interactive config for the following advanced options:
    # - args.settings_module
    # - args.secret_key
    # - args.static_root

    inform("Interactive configuration complete")

    args.save_settings = confirm("Save this configuration to\n" +
                                 yangsuite_prefs +
                                 "\nso YANG Suite can automatically use it"
                                 " next time you start YANG Suite?")


def inform(message):
    """Pretty-print a message to the user."""
    print('*' * 70)
    print(message)
    print('*' * 70)


def confirm(prompt, default_value='y'):
    """Prompt the user to confirm/deny the given prompt."""
    while True:
        response = get_input(prompt, default_value)
        if response == 'y' or response == 'Y':
            return True
        elif response == 'n' or response == 'N':
            return False
        else:
            print("Please enter 'y' or 'n'.")


def get_input(prompt, default_value):
    """Prompt the user for input."""
    response = None
    while not response:
        response = input("{0} [{1}] ".format(prompt, default_value))
        if not response:
            response = default_value
        if response:
            return response
        print("Please enter a valid value")


def configure_data_path(default_value):
    """Data path contains all user specific settings."""
    while True:
        path = get_input("YANG Suite stores user specific data "
                         "(YANG modules, device profiles, etc.)\n"
                         "Set new path or use:",
                         default_value=default_value)

        if path.startswith('~'):
            path = os.path.expanduser(path)
        else:
            path = os.path.abspath(path)
        if not os.path.isdir(path):
            create = confirm("Directory {0} does not exist. Create it?"
                             .format(path))
            if not create:
                continue
            os.makedirs(path)
        return path


def configure_file_path(prompt, default_value):
    """Path to a file YANG Suite uses. Includes private key and certificate."""
    while True:
        path = get_input("{0}\n"
                         "Set new file path or use:".format(prompt),
                         default_value=default_value)

        if os.path.isdir(path) or os.path.ismount(path):
            print("Please enter a valid file path (including filename).")
            continue

        if path.startswith('~'):
            path = os.path.expanduser(path)
        else:
            path = os.path.abspath(path)

        return path


def configure_port(default_value):
    """YANG Suite listening port."""
    while True:
        try:
            return int(get_input(
                "What port number should YANG Suite listen on?",
                default_value=default_value))
        except (TypeError, ValueError):
            print("Invalid port number.")


def get_suggested_addrs():
    """Get the list of suggested/example addresses to use."""
    ip_addresses = ['127.0.0.1']
    try:
        fqdn = socket.getfqdn()
        ip_addresses.insert(0, fqdn)

        try:
            hostname = socket.gethostname()
            if fqdn != hostname:
                ip_addresses.append(hostname)
        except socket.error:
            pass

        addrlist = socket.getaddrinfo(fqdn, None)
        # addrlist is a list of (family, stype, prot, '' ('addr', 'port',...))
        for addrtuple in addrlist:
            addr, port = addrtuple[4][:2]
            if addr not in ip_addresses:
                if addr:
                    ip_addresses.append(addr)
    except socket.error:
        pass
    return ip_addresses


def configure_access(default_value):
    """Allow YANG Suite to run on a remotes server."""
    inform("YANG Suite can be accessed remotely over the network.")
    if not confirm("Allow remote access?", default_value='n'):
        return default_value

    # Guess some values the user might want to configure
    ip_addresses = get_suggested_addrs()

    another_entry = True
    entries = []

    inform("Define hosts/IPs that YANG Suite will accept connections as.\n"
           "Examples:\n\t" + "\n\t".join(ip_addresses) +
           "\nIf the IP is not routable and you are behind NAT, "
           "use the public NAT address.")
    while another_entry:
        entry = get_input("Enter a hostname, FQDN, or address", '127.0.0.1')
        entries.append(entry)
        print("Entries so far: {0}".format(str(entries)))
        another_entry = confirm("Add another entry?", 'n')

    return entries


def create_private_key(path):
    """Create, save, and return a RSA private key.

    Create an RSA private key, store it in pem format at the given path, and return the key object.
    Return None if directories in the path do not exist (cannot save).
    """
    if not os.path.isdir(os.path.dirname(path)):
        inform("Failed to create private key. Path {0} does not exist."
               .format(os.path.split(path)[0]))
        return None

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    with open(path, 'wb') as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    return key


def create_certificate(path, key, addr):
    """Create, save, and return a x509 certificate.

    Create a self-signed x509 certificate using the passed key for the passed address,
    store it in pem format at the given path, and return the certificate object.
    Return None if directories in the path do not exist (cannot save).
    """
    if not os.path.isdir(os.path.dirname(path)):
        inform("Failed to create certificate. Path {0} does not exist."
               .format(os.path.split(path)[0]))
        return None

    # Prompt user for certificate details.
    country = get_input("Please enter your country code [XX]", 'US')
    state_province = get_input("Please enter your state/province", 'California')
    locality = get_input("Please enter your locality (city)", 'San Jose')
    organization = get_input("Please enter your organization name",
                             "Example Company Inc.")
    valid_days = int(get_input("Please enter the amount of days "
                               "the certificate should be valid for", 365))

    # Generate certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state_province),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.COMMON_NAME, addr),
    ])

    # Try to enter the address as an ip address. If exception is thrown,
    # enter it as a DNS name instead.
    try:
        name_obj = x509.IPAddress(ip_address(addr))
    except ValueError:
        name_obj = x509.DNSName(addr)

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=valid_days)
    ).add_extension(
        x509.SubjectAlternativeName([name_obj]),
        critical=False,
    ).sign(key, hashes.SHA256())

    # Save certificate to file at given certificate path.
    with open(path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    return cert


def load_private_key(path):
    """Load the key stored in pem format at the given path.

    Load the key stored in pem format at the given path.
    Return None if there is no file at the given path, or the file at the given path is not a
    pem format private key.
    """
    if not os.path.isfile(path):
        return None

    try:
        with open(path, 'rb') as f:
            key = serialization.load_pem_private_key(f.read(), None)
    except ValueError:
        inform("File at {0} could not be serialized. "
               "The file is not a pem format private key file.".format(path))
        return None
    return key


def load_certificate(path):
    """Load the x509 certificate stored in pem format at the given path.

    Load the x509 certificate stored in pem format at the given path.
    Return None if there is no file at the given path, or the file at the given path is not a
    pem format x509 certificate.
    """
    if not os.path.isfile(path):
        return None

    try:
        with open(path, 'rb') as f:
            cert = x509.load_pem_x509_certificate(f.read())
    except ValueError:
        inform("File at {0} could not be loaded. "
               "The file is not a pem format x509 certificate file.".format(path))
        return None
    return cert


def verify_certificate(key, cert):
    """Verify that the passed certificate was signed by the passed private key.

    Verify that the passed certificate (object) was signed by the passed private key (object).
    Returns the certificate (object) if true, and None type if not.
    """
    try:
        key.public_key().verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            cert.signature_algorithm_parameters,
            cert.signature_hash_algorithm
        )
    except InvalidSignature:
        inform("Certificate was not signed by given private key, and thus cannot be used.")
        return None
    return cert


def check_eula(user):
    """Check if user has agreed to Cisco General Terms."""
    cfg = read_prefs()
    prefs = cfg[configparser.DEFAULTSECT]
    return prefs.get('eula_agreement', '') == 'accepted'


def call_eula(prefs):
    """Cisco EULA agreement set from CLI."""
    eula_link = ('https://www.cisco.com/c/dam/en_us/'
                 'about/doing_business/legal/Cisco_General_Terms.pdf')
    webbrowser.open(eula_link, new=2)
    resp = input(
        'Do you accept the terms and conditions stated in the "Cisco General \
Terms? <accept/no>: ')
    while resp not in ['accept', 'no', 'n']:
        resp = input(
            'Please type "accept" to accept the agreement or "no" to decline'
        )
    if resp != 'accept':
        if os.path.isdir('build'):
            shutil.rmtree('build')
        cmd = ["pip", "uninstall", "yangsuite"]
        try:
            import ysdevices    # noqa
            cmd.append("yangsuite-devices")
        except ImportError:
            pass
        try:
            import ysfilemanager    # noqa
            cmd.append("yangsuite-filemanager")
        except ImportError:
            pass
        try:
            import ysyangtree    # noqa
            cmd.append("yangsuite-yangtree")
        except ImportError:
            pass
        try:
            import ysnetconf    # noqa
            cmd.append("yangsuite-netconf")
        except ImportError:
            pass
        cmd.append("-y")
        subprocess.run(cmd)
        exit(1)
    else:
        prefs['eula_agreement'] = 'accepted'


if __name__ == "__main__":
    main()
