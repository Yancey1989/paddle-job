# PaddlePaddel Job
Submit PaddlePaddle distributed traininig job to Kubernetes cluster

## Usage
- Initialize `PaddleJob`
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
    cephfs_volume=CephVolume())
  ```
- Local Training and Distributed Traininig

  If you want to start a local training job, according with PaddlePaddle v2 API
  ```python
  trainer.train(reader=reader, num_passes=100, ...)
  ```
  Otherwise, you can call `job.dist_train` to submit a distributed training job
  ```python
  job.dist_train(trainer=trainer, reader=reader, paddle_job=paddle_job)
  ```

## Parameters

- `PaddleJob` Parameters

parameter | required | default | explain
  --- | --- | --- | ---
job_name|YES||you should special a uniq job name which in a namespace
trainer_package|YES|| entry point for startup trainer process
input| YES || input directory on distributed file system
output|YES|| output directory on distributed file system
pservers|YES|| parameter server process count
base-image|YES||PaddlePaddle production Docker image
memory|YES|| limits for memory
use_gpu|NO|False| whether use GPU
cpu_num|NO|1| if `use_gpu=false`, this parameter is required
gpu_num|NO|1| if `use_gpu=true`, this parameter is required
cephfs_volume|NO|None|CephFS volume configuration

- `CephFSVolume` Parameters

  If you want to use CephFS as your distributed storage,
 you can configurat CephFSVolume with parameters or export environment variables.

parameter | required | default | environment |explain
 --- | --- | --- | --- | ---
 monitors_addr| YES | | CEPHFS_MONITOR_ADDRS| ceph cluster monitor addres
user | YES| admin |CEPHFS_USER|ceph user name
secret_name | YES |ceph-secret | CEPHFS_SECRET | ceph secret name in kubernetes
mount_path | NO | /mnt/cephfs | CEPHFS_MOUNT_PATH | CephFS mount path in Pod
