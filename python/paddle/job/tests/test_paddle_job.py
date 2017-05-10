import unittest
import paddle.job as job
from paddle.job import CephFSVolume
class PaddleJobTest(unittest.TestCase):
    def __new_paddle_job(self):
        return job.PaddleJob(
            runtime_image="yancey1989/paddle-job",
            job_name="paddle-job",
            cpu_nums=3,
            trainer_package="/example/word2vec",
            entry_point="python train.py",
            cephfs_volume=job.CephFSVolume(
                monitors_addr="172.19.32.166:6789"
            ))
    def test_runtime_image(self):
        paddle_job=self.__new_paddle_job()
        self.assertEqual(paddle_job._runtime_image, "yancey1989/paddle-job")

    def test_new_pserver_job(self):
        paddle_job=self.__new_paddle_job()
        pserver_job = paddle_job.new_pserver_job()
        self.assertEqual(pserver_job["metadata"]["name"], "paddle-job-pserver")

    def test_new_trainer_job(self):
        paddle_job=self.__new_paddle_job()
        pserver_job = paddle_job.new_trainer_job()
        self.assertEqual(pserver_job["metadata"]["name"], "paddle-job-trainer")

if __name__=="__main__":
    unittest.main()
