# PaddlePaddel Job
向Kubernetes集群提交一个PaddlePaddle的分布式任务

## Usage
```python
import paddle.job as job
from job.job_manager import JobManager
from job.paddle_job import PaddleJob

paddle_job = PaddleJob(
      trainers=3,
      pservers=3,
      base_image="yancey1989/paddle-cloud",
      glusterfs_volume="gfs_vol",
      input="/yanxu05",
      output="/yanxu05",
      job_name="paddle-cloud",
      namespace="yanxu",
      use_gpu=False,
      port=7164,
      ports_num=1,
      ports_num_for_sparse=1,
      num_gradient_servers=1,
      trainer_package_path="/yanxu05/word2vec",
      entry_point="python api_train_v2.py")

jm = JobManager(paddle_job)
jm.submit()

```
