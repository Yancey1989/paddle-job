import kubernetes
from kubernetes import client, config
import os
import paddle.job
__all__ = ["PaddleJob"]


class PaddleJob(object):
    """
        PaddleJob
    """

    def __init__(self,
                 job_name,
                 trainer_package,
                 entry_point,
                 runtime_image,
                 cpu_nums,
                 memory="1G",
                 gpu_nums=0,
                 cephfs_volume=None,
                 trainers=-1,
                 pservers=-1):

        self._port=7164
        self._ports_num=1
        self._ports_num_for_sparse=1
        self._num_gradient_servers=1

        self._job_name = job_name
        self._trainer_package = trainer_package
        self._entry_point = entry_point
        self._runtime_image = runtime_image
        self._cpu_nums = cpu_nums
        self._memory = memory
        self._gpu_nums = gpu_nums
        self._cephfs_volume = cephfs_volume
        self._namespace = "default"
        self._trainers=3
        self._pservers=3

    @property
    def pservers(self):
        return self._pservers

    @property
    def trainers(self):
        return self._trainers

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        self._namespace = namespace

    @property
    def runtime_image(self):
        return self._runtime_image

    def _get_pserver_job_name(self):
        return "%s-pserver" % self._job_name

    def _get_trainer_job_name(self):
        return "%s-trainer" % self._job_name

    def get_env(self):
        envs = []
        envs.append({"name":"PADDLE_JOB_NAME",      "value":self._job_name})
        envs.append({"name":"TRAINERS",             "value":str(self._get_trainers())})
        envs.append({"name":"PSERVERS",             "value":str(self._pservers)})
        envs.append({"name":"ENTRY_POINT",          "value":self._entry_point})
        envs.append({"name":"TRAINER_PACKAGE",      "value":self._trainer_package})
        envs.append({"name":"RUNNING_ON_CLOUD",     "value":"YES"})
        envs.append({"name":"PADDLE_INIT_PORT",     "value":str(self._port)})
        envs.append({"name":"PADDLE_INIT_TRAINER_COUNT",        "value":"1"})
        envs.append({"name":"PADDLE_INIT_PORTS_NUM",            "value":str(self._ports_num)})
        envs.append({"name":"PADDLE_INIT_PORTS_NUM_FOR_SPARSE", "value":str(self._ports_num_for_sparse)})
        envs.append({"name":"PADDLE_INIT_NUM_GRADIENT_SERVERS", "value":str(self._num_gradient_servers)})
        envs.append({"name":"NAMESPACE", "valueFrom":{
            "fieldRef":{"fieldPath":"metadata.namespace"}}})
        return envs

    def _get_pserver_container_ports(self):
        ports = []
        port = self._port
        for i in xrange(self._ports_num + self._ports_num_for_sparse):
            ports.append({"containerPort":port, "name":"jobport-%d" % i})
            port += 1
        return ports

    def _get_pserver_labels(self):
        return {"paddle-job": self._get_pserver_job_name()}

    def _get_pserver_entrypoint(self):
        return ["paddle_k8s", "start_pserver"]

    def _get_trainer_entrypoint(sefl):
        return ["paddle_k8s", "start_trainer"]

    def _get_trainers(self):
        if self._gpu_nums:
            return self._gpu_nums
        return self._cpu_nums

    def _get_trainer_labels(self):
        return {"paddle-job": self._get_trainer_job_name()}


    def _get_trainer_volumes(self):
        volumes = []
        if self._cephfs_volume:
            volumes.append(self._cephfs_volume.volume)
        return volumes

    def _get_trainer_volume_mounts(self):
        volume_mounts = []
        if self._cephfs_volume:
            volume_mounts.append(self._cephfs_volume.volume_mount)
        return volume_mounts

    def new_trainer_job(self):
        """
        return: Trainer job, it's a Kubernetes Job
        """
        return {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": self._get_trainer_job_name(),
            },
            "spec": {
                "parallelism": self._get_trainers(),
                "completions": self._get_trainers(),
                "template": {
                    "metadata":{
                        "labels": self._get_trainer_labels()
                    },
                    "spec": {
                        "volumes": self._get_trainer_volumes(),
                        "containers":[{
                            "name": "trainer",
                            "image": self._runtime_image,
                            "imagePullPolicy": "Always",
                            "command": self._get_trainer_entrypoint(),
                            "env": self.get_env(),
                            "volumeMounts": self._get_trainer_volume_mounts()
                        }],
                        "restartPolicy": "Never"
                    }
                }
            }
        }
    def new_pserver_job(self):
        """
        return: PServer job, it's a Kubernetes ReplicaSet
        """
        return {
            "apiVersion": "extensions/v1beta1",
            "kind": "ReplicaSet",
            "metadata":{
                "name": self._get_pserver_job_name(),
            },
            "spec":{
                "replicas": self._pservers,
                "template": {
                    "metadata": {
                        "labels": self._get_pserver_labels()
                    },
                    "spec": {
                        "containers":[{
                            "name": self._get_pserver_job_name(),
                            "image": self._runtime_image,
                            "ports": self._get_pserver_container_ports(),
                            "env": self.get_env(),
                            "command": self._get_pserver_entrypoint()
                        }]
                    }
                }
            }
        }
