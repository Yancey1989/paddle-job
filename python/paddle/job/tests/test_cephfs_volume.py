import unittest
from paddle.job import CephFSVolume
class CephFSVolumeTest(unittest.TextCase):
    def test_get_volume(self):
        cephfs_volume = CephFSVolume()
        self.assertEqual(cephfs_volume.get_volume()["path"] , "/")
if __name__=="__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(CephFSVolumeTest)
    unittest.TextTestRunner().run(suite)
    
