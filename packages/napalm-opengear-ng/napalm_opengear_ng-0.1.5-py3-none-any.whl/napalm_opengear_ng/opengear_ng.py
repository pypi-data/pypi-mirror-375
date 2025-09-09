"""NAPALM driver for Opengear CM81xx"""

import re
import socket
import string
import tempfile
from collections import defaultdict

from napalm.base import NetworkDriver
from napalm.base.exceptions import (
    CommandErrorException,
    MergeConfigException,
)
from napalm.base.netmiko_helpers import netmiko_args
from netmiko import ConnectHandler, FileTransfer

METHODS_MAP = {
    "merge": "import",
    "replace": "restore",
}


class OpengearNGDriver(NetworkDriver):
    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        self.device = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout
        self.changed = False
        self.config_method = None
        self.config_file = False

        if optional_args is None:
            optional_args = {}

        self.optional_args = optional_args

        self.netmiko_optional_args = netmiko_args(optional_args)

    def _get_interfaces_list(self):
        show_int = self.device.send_command(
            "ip link|awk '/^[0-9]: [a-z]/ {print $2}'|tr -d :"
        )
        return show_int.splitlines()

    def open(self):
        """Open a connection to the device."""
        self.device = ConnectHandler(
            device_type="linux",
            host=self.hostname,
            username=self.username,
            password=self.password,
            secret=self.password,
            **self.netmiko_optional_args,
        )
        if self.username != "root":
            self.device.enable()

    def close(self):
        if self.config_file:
            # cleanup candidate and backup files, ignore errors
            self.device.send_command(
                "rm -rf /var/tmp/candidate-napalm.sh /var/tmp/backup-napalm.sh || true"
            )
        self._netmiko_close()

    def is_alive(self):
        null = chr(0)
        if self.device is None:
            return {"is_alive": False}

        try:
            # Try sending ASCII null byte to maintain the connection alive
            self.device.write_channel(null)
            return {"is_alive": self.device.remote_conn.transport.is_active()}
        except (socket.error, EOFError):
            # If unable to send, we can tell for sure that the connection is unusable
            return {"is_alive": False}

        return {"is_alive": False}

    def get_facts(self):
        """Get facts from the device."""
        facts = {
            "uptime": -1.1,
            "vendor": "Unknown",
            "os_version": "Unknown",
            "serial_number": "Unknown",
            "model": "Unknown",
            "hostname": "Unknown",
            "fqdn": "Unknown",
            "interface_list": [],
        }

        uptime = self.device.send_command("cat /proc/uptime")
        facts["uptime"] = float(uptime.split()[0])

        get_version = self.device.send_command("cat /etc/os-release")
        for line in get_version.splitlines():
            if line.startswith("ID="):
                facts["vendor"] = line.split("=")[1].strip().strip('"')
            elif line.startswith("VERSION_ID="):
                facts["os_version"] = line.split("=")[1]

        system_info = self.device.send_command("ogcli get system/info")
        for line in system_info.splitlines():
            if "model_name=" in line:
                facts["model"] = line.split("=")[1].strip().strip('"')
            elif "serial_number=" in line:
                facts["serial_number"] = line.split("=")[1].strip().strip('"')

        hostname = self.device.send_command("ogcli get system/hostname")
        for line in hostname.splitlines():
            if "hostname=" in line:
                facts["hostname"] = line.split("=")[1].strip().strip('"')

        fqdn = self.device.send_command("hostname -f")
        facts["fqdn"] = fqdn.strip()

        facts["interface_list"] = self._get_interfaces_list()

        return facts

    def get_interfaces_ip(self):
        interfaces_list = self._get_interfaces_list()

        interface_ips = dict()
        for interface in interfaces_list:
            interface_ips[interface] = {"ipv4": {}, "ipv6": {}}
            for af in (4, 6):
                ips = self.device.send_command(
                    f"ip -{af} addr show {interface} | grep -oP '(?<=inet\s)\S+|(?<=inet6\s)\S+'"
                )
                for address in ips.strip().splitlines():
                    ipe = address.split("/")
                    interface_ips[interface][f"ipv{af}"][ipe[0].strip()] = {
                        "prefix_length": int(ipe[1].strip()),
                    }
        return interface_ips

    def get_interfaces(self):
        interfaces_list = self._get_interfaces_list()

        interfaces = {}
        for interface in interfaces_list:
            iface_link = self.device.send_command(f"ip link show {interface}")

            iface = {
                "is_enabled": True,
                "is_up": False,
                "description": "",
                "mac_address": "",
                "last_flapped": 0.0,  # in seconds
                "speed": 0.0,  # in megabits
                "mtu": 0,
            }
            mtu = re.compile("mtu (\d+)")
            for line in iface_link.splitlines():
                if "state UP" in line:
                    iface["is_up"] = True
                elif "link/ether" in line:
                    iface["mac_address"] = line.split()[1].strip()
                mtu_match = mtu.search(line)
                if mtu_match:
                    iface["mtu"] = int(mtu_match.group(1))

            iface_eth = self.device.send_command("ethtool " + str(interface))
            for line in iface_eth.splitlines():
                if "Speed:" in line:
                    try:
                        iface["speed"] = float(line.split()[1].strip("Mb/s"))
                    except ValueError:
                        iface["speed"] = 0.0

            interfaces[interface] = iface

        return interfaces

    def get_config(self, retrieve="all", sanitized=False):
        # Retrieve configuration from the device, startup and running should always be the same
        config = {
            "startup": "",
            "running": "",
            "candidate": "",
        }

        if retrieve == "candidate":
            raise NotImplementedError(
                "Candidate configuration retrieval is not implemented."
            )
        command = "ogcli export"
        if sanitized:
            command = "ogcli --secrets mask export"
        current_config = self.device.send_command(command, read_timeout=120)
        if retrieve in ("running", "all"):
            config["running"] = current_config
        if retrieve in ("startup", "all"):
            config["startup"] = current_config

        return config

    def _load_config(self, filename=None, config=None):
        if not filename and not config:
            raise MergeConfigException("No configuration provided to load.")
        elif config:
            if isinstance(config, list):
                config = "\n".join(config)
            with tempfile.NamedTemporaryFile(
                "w+", delete=False, encoding="utf-8"
            ) as temp_config:
                temp_config.write(config)
                temp_config.flush()
                filename = temp_config.name

        transfer = FileTransfer(
            ssh_conn=self.device,
            source_file=filename,
            dest_file="candidate-napalm.sh",
        )
        try:
            transfer.establish_scp_conn()
            transfer.transfer_file()
        except Exception as e:
            raise MergeConfigException(f"Failed to transfer config file: {e}") from e

        if not transfer.check_file_exists():
            raise MergeConfigException("Failed to transfer config file.")
        transfer.close_scp_chan()
        self.config_file = f"{transfer.file_system}/{transfer.dest_file}"
        return True

    def _load_candidate(self, method, **kwargs):
        self.config_method = method
        if self.config_method not in METHODS_MAP:
            raise NotImplementedError(
                f"{self.config_method} candidate configuration is not implemented."
            )
        if not self.config_file:
            if not self._load_config(**kwargs):
                raise MergeConfigException("Failed to load candidate configuration.")

        backup = self.device.send_command("ogcli export /var/tmp/backup-napalm.sh")
        if backup.strip() != "":
            raise CommandErrorException(f"Could not backup configuration:\n{backup}")
        return True

    def load_merge_candidate(self, filename=None, config=None, **kwargs):
        return self._load_candidate("merge", filename=filename, config=config, **kwargs)

    def load_replace_candidate(self, filename=None, config=None, **kwargs):
        return self._load_candidate(
            "replace", filename=filename, config=config, **kwargs
        )

    def compare_config(self, filename=None, config=None):
        if not self.config_file:
            if not self._load_config(filename=filename, config=config):
                raise MergeConfigException("Failed to load candidate configuration.")

        compare_config = self.device.send_command(
            f"ogcli diff {self.config_file}", read_timeout=60
        ).strip()

        if "was an error" in compare_config:
            raise MergeConfigException(
                f"Failed to compare configuration:\n{compare_config}"
            )

        return compare_config

    def commit(self):
        if not self.config_file or not self.config_method:
            raise MergeConfigException(
                "No candidate configuration to commit, load configuration first."
            )

        apply_config = self.device.send_command(
            f"ogcli {METHODS_MAP[self.config_method]} {self.config_file}",
            read_timeout=60,
        )

        ok_char = string.printable
        # When the device is importing a config, it spits a message everys seconds
        # filtering them out (also empty lines)
        output = [
            line
            for line in apply_config.splitlines()
            if line.strip() and line[0] in ok_char
        ]
        success = re.compile(rf"{'|'.join(METHODS_MAP.values())} successful")
        if not any(success.match(line) for line in output):
            raise MergeConfigException(
                f"Could not merge configuration:\n{apply_config}"
            )
        return True
