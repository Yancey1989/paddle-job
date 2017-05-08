from utils import get_parameter
__all__ = ["CephFSVolume"]


class CephFSVolume(object):
    def __init__(self, monitors_addr=None, user=None, secret_name=None, mount_path=None, cephfs_path=None):
        self.monitors = get_parameter(monitors_addr, "CEPHFS_MONITORS_ADDR", "").split(",")
        self.user = get_parameter(user, "CEPHFS_USER", "admin")
        self.secret_name = get_parameter(secret_name, "CEPHFS_SECRET", "cephfs-secret")
        self.mount_path = get_parameter(mount_path, "CEPHFS_MOUNT_PATH", "/mnt/cephfs")
        self.cephfs_path = get_parameter(cephfs_path, "CEPHFS_PATH", "/")


    def get_volume(self):
        return {
            "name": "cephfs",
            "monitors": self.monitors,
            "path": self.cephfs_path,
            "user": self.user,
            "secretRef": {
                "name": self.secret_name
            }
        }

    def get_volume_mount(self):
        return {
            "mount_path": self.mount_path,
            "name": "cephfs"
        }
