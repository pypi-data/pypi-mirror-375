import pickle

from linux.base_objects import LinuxHost

from firewheel.control.experiment_graph import require_class


@require_class(LinuxHost)
class NTPServer:
    """
    This Object can be used to decorate a VM and install
    the NTP service on the VM to provide NTP within the experiment.
    """

    def __init__(self):
        """
        Create the NTP configuration and install the NTP service
        on the given VM.
        """
        config = {
            "ntp": {
                "conf_dir": "/etc",
                "service_name": "ntp",
                "config_file_name": "ntp.conf",
                "conf_files": {
                    "ntp.conf": """server 127.127.1.0
fudge 127.127.1.0 stratum 0"""
                },
            }
        }

        pickled_config = pickle.dumps(config["ntp"], protocol=0).decode()
        self.add_vm_resource(
            -101, "install_linux_service.py", pickled_config, "ntp-trusty-server.tgz"
        )
