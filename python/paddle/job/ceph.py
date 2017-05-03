
__all__ = ["CephVolume"]

class CephVolume(object):
    def __init__(self, monitors_addr=None, user=None, secret_name=None):
        self.monitors = get_parameter(monitors_addr, "CEPH_MONITOR_ADDRS").split(",")
        self.user = get_parameter(user, "CEPH_USER")
        self.secret_name = get_parameter(secret_name, "CEPH_SECRET")

    @property
    def monitors(self):
        return self.monitors

    @property
    def user(self):
        return self.user

    @property
    def secret_name(self):
        return self.secret_name
