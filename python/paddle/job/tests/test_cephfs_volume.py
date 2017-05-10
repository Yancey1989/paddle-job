import unittest
from paddle.job import CephFSVolume
class CephFSVolumeTest(unittest.TestCase):
    def test_get_volume(self):
        cephfs_volume = CephFSVolume()
        self.assertEqual(cephfs_volume.volume["name"] , "cephfs")
if __name__=="__main__":
    unittest.main()
