
__all__ = ["CephFSVolume"]

CEPHFS_MOUNT_PATH="/mnt/cephfs"

class CephFSVolume(object):
    def __init__(self, monitors_addr=None, user=None, secret_name=None, mount_path=None):
        self.monitors = get_parameter(monitors_addr, "CEPHFS_MONITORS_ADDR").split(",")
        self.user = get_parameter(user, "CEPHFS_USER")
        self.secret_name = get_parameter(secret_name, "CEPHFS_SECRET")
        self.mount_path = get_parameter(mount_path, "CEPHFS_MOUNT_PATH")


    @property
    def monitors(self):
        return self.monitors

    @property
    def user(self):
        return self.user

    @property
    def secret_name(self):
        return self.secret_name

    def get_volume(self):
        return {
            "name": "cephfs",
            "monitors": self.ceph_volume.monitors,
            "path": "/",
            "user": self.ceph_volume.user,
            "secretRef": {
                "name": self.ceph_volume.secret_name
            }
        }

    def get_volume_mount(self):
        return {
            "mount_path": CEPHFS_MOUNT_PATH,
            "name": "cephfs"
        }
