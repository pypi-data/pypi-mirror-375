from reemote.result import Result

class Directory:
    class Directory:
        """
        A class to manage directory states on a filesystem.

        Attributes:
            path (str): The absolute or relative path of the directory to manage. This is the target directory whose state will be checked or modified.
            present (bool): Indicates whether the directory should exist (`True`) or not (`False`) on the system. If `True`, the directory will be created if it does not exist. If `False`, the directory will be removed if it exists.
            sudo (bool): If `True`, the commands will be executed with `sudo` privileges. Defaults to `False`.
            su (bool): If `True`, the commands will be executed with `su` privileges.

        Usage:
            This class is designed to be used in a generator-based workflow where commands are yielded for execution.
            It supports creating or removing directories based on the `present` flag and allows privilege escalation via `sudo`.

        Notes:
            - Commands are constructed based on the `present` and `sudo` flags.
            - The `changed` flag is set if the directory state changes after execution.
        """
    def __init__(self, path: str, present: bool, sudo: bool = False, su: bool = False):
        self.path = path
        self.present = present
        self.sudo = sudo
        self.su = su

    def __repr__(self):
        return (f"Directory(path={self.path!r}, present={self.present!r},"
               f"sudo={self.sudo!r}, su={self.su!r})")

    def execute(self):
        r0 = yield f"composite {self}"
        _sudo: str = "sudo -S " if self.sudo else ""
        _su: str = "su -c " if self.su else ""

        # Check whether the directory exists
        r1: Result = yield f"{_sudo}[ -d {self.path} ]"
        # print(f">>>>> Received in Directory: {r}")

        if self.present and r1.cp.returncode != 0:
            # Present directory does not exist, so create it
            r2 =yield f"{_sudo}mkdir -p {self.path}"
            # print(f">>>>> Received in Directory: {r1}")
            r2.changed = True
            r0.changed = True

        if not self.present and r1.cp.returncode == 0:
            # Not Present directory exists, so remove it
            r3 = yield f"{_sudo}rmdir -p {self.path}"
            # print(f">>>>> Received in Directory: {r2}")
            r3.changed = True
            r0.changed = True
