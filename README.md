# PaddlePaddel Job
Submit PaddlePaddle distributed traininig job to Kubernetes cluster

## Usage
1. Initial `PaddleJob`
  ```python
  import paddle.job as job
  paddle_job = job.PaddleJob(
    pservers=3,
    base_image="yancey1989/paddle-cloud",
    input="/yanxu05",
    output="/yanxu05",
    job_name="paddle-cloud",
    namespace="yanxu",
    use_gpu=False,
    cpu_num=3,
    memory="1G"
    trainer_package_path="/yanxu05/word2vec",
    entry_point="python api_train_v2.py",
    ceph_volume=CephVolume())
  ```
1. Call `job.dist_train`, instead of `trainer.train`
  ```python
  job.dist_train(
    trainer=trainer,
    reader=reader,
    paddle_job=job)
  ```

## `PaddleJob` parameters description

parameter | required | default | explain
  --- | --- | --- | ---
job_name|YES||you should special a uniq job name which in a namespace
trainer_package|YES|| entry point for startup trainer process
input| YES || input directory on distributed file system
output|YES|| output directory on distributed file system
pservers|YES|| parameter server process count
base-image|YES||PaddlePaddle production Docker image
memory|YES|| limits for memory
use_gpu|NO|false| whether use GPU
cpu_num|NO|1| if `use_gpu=false`, this parameter is required
gpu_num|NO|1| if `use_gpu=true`, this parameter is required
