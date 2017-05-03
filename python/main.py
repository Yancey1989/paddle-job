from job.job_manager import JobManager
from job.paddle_job import PaddleJob
paddle_job = PaddleJob(trainers=3,
                       pservers=3,
                       base_image="yancey1989/paddle-k8s",
                       glusterfs_volume="gfs_vol",
                       input="/yanxu05",
                       output="/yanxu05",
                       job_name="paddle-cloud",
                       namespcae="default",
                       paddle_port=7614,
                       paddle_port_num=2,
                       paddle_port_num_sparse=2)
job_manager = JobManager(paddle_job=paddle_job)
job_manager.submit()
