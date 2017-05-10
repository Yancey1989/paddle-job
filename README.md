# PaddlePaddel Job
Running PaddlePaddle distributed training job on Kubernetes cluster.

## Usage
### Prepare Training Data
  You can implement a distributed dataset with `reader function`, an example:
  ```python
  def dataset_from_reader(filename, reader):
      with open(filename, "w") as fn:
          for batch_id, batch_data in enumerate(reader()):
              batch_data_str = [str(d) for d in batch_data]
              fn.write(",".join(batch_data_str))
              fn.write("\n")
  ```
  An complete example for dataset: [imikolov](https://github.com/PaddlePaddle/Paddle/blob/develop/python/paddle/v2/dataset/imikolov.py) is [here](./example/word2vec/prepare.py)

### Submit PaddleJob with Python Code
  If you haven't configurated `kubectl`, do as this [tutorail](https://github.com/k8sp/tutorials/blob/develop/configure_kubectl.md) please.
- Fetch Runtime information:
  - *trainer id*, the unique id for each trainer, you can fetch current trainer id from environment variable `TRAINER_ID`
  - *trainer count*, the trainer process count, you can fetch this one from environment variable `TRAINERS`
- Dist Reader Interface

  You can implement a `dist_reader` to reading data when the trainer is running on Kubernetes.
  An example implemention for dist reader creator:
  ```python
  def dist_reader(filename, trainers, trainer_id):
      def dist_reader_creator():
          with open (filename) as f:
              cnt = 0
              for line in f:
                  cnt += 1
                  if cnt % trainers == trainer_id:
                      csv_data = [int(cell) for cell in line.split(",")]
                      yield tuple(csv_data)
      return dist_reader_creator
  ```
  *NOTE*: You can read files from CephFS on directory: `/data/...`
- Create [PaddleJob](#paddlejob-parameters) instance
  ```python
  import paddle.job as job
  paddle_job=job.PaddleJob(
      pservers=3,
      runtime_image="yancey1989/paddle-job",
      job_name="paddle-job",
      namespace="yanxu",
      use_gpu=False,
      cpu_num=3,
      trainer_package_path="/example/word2vec",
      entry_point="python train.py",
      cephfs_volume=job.CephFSVolume(
          monitors_addr="172.19.32.166:6789"
      ))  
  ```
- Build Runtime Docker Image on Base Docker Image

  You can build a runtime Docker Image with the tools: `./tools/build_docker.sh`, such as:
  ```bash
  ./tools/build_docker.sh <src_trainer_package> <dest_trainer_package> <base Docker image> <runtime Docker image>
  ```
  - *src_trainer_package*, the trainer package on your host.
  - *dest_trainer_package* is an absolute path, copies the src_trainer_package to the filesystem of the image at the path dest_trainer_package
  - *base Docker image* is PaddlePaddle product Docker image including paddle binary files and python packages. And of course, you can specify and image name hosted on any docker registry which users have the access right.
  - *runtime Docker image* your train package files are packaged into the runtime Docker image on base Docker image.
  Example:
  ```bash
  ./tools/build_docker.sh ./example/ /example paddlepaddle/paddle yancey1989/paddle-job
  ```
- Push the Runtime Docker Image

  You can push your Runtime Docker Image to Docker registry server
  ```bash
  docker push <runtime Docker image>
  ```
  Example:
  ```bash
  docker push yancey1989/paddle-job
  ```
- Submit Distributed Job

  ```bash
  docker run --rm -it -v $HOME/.kube/config:/root/.kube/config <runtime image name> <entry point>
  ```
  Example:
  ```bash
  docker run --rm -it -v $HOME/.kube/config:/root/.kube/config python /example/train.py
  ```

## PaddlePaddle Job Configuration

### PaddleJob parameters
- Required Parameters

parameter | type | explanation
--- | --- | ---
job_name | string | the unique name for the training job
entry_point | string |entry point for startup trainer process
memory | string | memory allocated for the job, a plain integer using one of these suffixes: E, P, T, G, M, K
cpu_nums | int | CPU count for the job
runtime_image | string | runtime Docker image

- Advanced Parameters

parameter | type | default | explanation
  --- | --- | --- | ---
pservers | int | 2 | Parameter Server process count
trainers | int | 3 | Trainer process count
gpu_nums | int | 0 | GPU count for the job
cephfs_volume| CephFSVolume | None | CephFS volume configuration


### CephFSVolume parameters
- Required Parameters

parameter | type | explanation
--- | --- | ---
monitors_addr | string | the address for Ceph cluster monitors.

- Advanced Parameters

parameter | type | default | explanation
--- | --- | --- | ---
user | string | admin |Ceph cluster user name
secret_name | string | cephfs-secret|Ceph cluster secret, it's Kubernetes Secret name
mount_path | string  | `/mnt/cephfs` |CephFS mount path in Pod
path | string | `/` |CephFS path
