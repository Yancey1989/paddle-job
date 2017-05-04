import kubernetes
from kubernetes import client, config
import os

__all__ = ["PaddleJob"]

## kubernetes default configuration
DEFAULT_GLUSTERFS_ENDPOINT = "glusterfs-cluster"
GLUSTERFS_MOUNT_PATH = "/mnt/glusterfs"


class PaddleJob(object):
    """
        PaddleJob
    """

    def __init__(self,
                 pservers,
                 base_image,
                 input,
                 output,
                 job_name,
                 trainer_package_path,
                 entry_point,
                 namespace="default",
                 use_gpu=False,
                 cpu_num=1,
                 gpu_num=1,
                 memory="1G",
                 num_gradient_servers=1,
                 port=7164,
                 ports_num=1,
                 ports_num_for_sparse=1,
                 ceph_volume=None):
        self.pservers = pservers
        self.base_iamge = base_image
        self.input = input
        self.output = output
        self.job_name = job_name
        self.namespace = namespace
        self.ports_num = ports_num
        self.ports_num_for_sparse = ports_num_for_sparse
        self.port = port
        self.use_gpu = use_gpu
        self.trainer_package_path = trainer_package_path
        self.entry_point = entry_point
        self.num_gradient_servers = num_gradient_servers
        self.cpu_num = cpu_num
        self.gpu_num = gpu_num
        self.ceph_volume = ceph_volume
        self.memory = memory

    def _get_pserver_job_name(self):
        return "%s-pserver" % self.job_name

    def _get_trainer_job_name(self):
        return "%s-trainer" % self.job_name

    def get_env(self):
        envs = []
        envs.append({"name":"PADDLE_JOB_NAME",      "value":self.job_name})
        envs.append({"name":"PORT",                 "value":str(self.port)})
        envs.append({"name":"TRAINERS",             "value":str(self._get_trainers())})
        envs.append({"name":"PSERVERS",             "value":str(self.pservers)})
        envs.append({"name":"PORTS_NUM",            "value":str(self.ports_num)})
        envs.append({"name":"PORTS_NUM_FOR_SPARSE", "value":str(self.ports_num_for_sparse)})
        envs.append({"name":"NUM_GRADIENT_SERVERS", "value":str(self.num_gradient_servers)})
        envs.append({"name":"OUTPUT",               "value":self.output})
        envs.append({"name":"ENTRY_POINT",          "value": self.entry_point})
        envs.append({"name":"TRAINER_PACKAGE_PATH",
                     "value":os.path.join(GLUSTERFS_MOUNT_PATH,
                           self.trainer_package_path.lstrip("/"))})
        envs.append({"name":"NAMESPACE", "value_from":{
            "field_ref":{"field_path":"metadata.namespace"}}})
        return envs

    def _get_pserver_container_ports(self):
        ports = []
        port = self.port
        for i in xrange(self.ports_num + self.ports_num_for_sparse):
            ports.append({"containerPort":port, "name":"jobport-%d" % i})
            port += 1
        return ports

    def _get_pserver_labels(self):
        return {"paddle-job": self._get_pserver_job_name()}

    def _get_pserver_entrypoint(self):
        return ["paddle_k8s", "start_pserver"]

    def _get_trainer_entrypoint(sefl):
        return ["paddle_k8s", "start_trainer"]

    def _get_runtime_docker_image_name(self):
        #TODO: use runtime docker image
        return self.base_iamge
        #return "%s-%s:latest" % (self.namespace, self.job_name)

    def _get_trainers(self):
        if self.use_gpu:
            return self.gpu_num if self.gpu_num else 1
        else:
            return self.cpu_num if self.cpu_num else 1

    def _get_trainer_labels(self):
        return {"paddle-job": self._get_trainer_job_name()}


    def _get_trainer_volumes(self):
        volumes = []
        if self.ceph_volume:
            volumes.append(self.ceph_volume.get_volume())
        return volumes

    def _get_trainer_volume_mounts(self):
        volume_mounts = []
        if self.ceph_volume:
            volume_mounts.append(self.ceph_volume.get_volume_mount())
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
                            "image": self._get_runtime_docker_image_name(),
                            "image_pull_policy": "Always",
                            "command": self._get_trainer_entrypoint(),
                            "env": self.get_env(),
                            "volume_mounts": self._get_trainer_volume_mounts()
                        }],
                        "restartPolicy": "Never"
                    }
                }
            }
        }
    def new_pserver_job(self):
        """
        return: PServer job, it's a Kubernetes StatefulSet
        """
        return {
            "apiVersion": "apps/v1beta1",
            "kind": "StatefulSet",
            "metadata":{
                "name": self._get_pserver_job_name(),
            },
            "spec":{
                "serviceName": self._get_pserver_job_name(),
                "replicas": self.pservers,
                "template": {
                    "metadata": {
                        "labels": self._get_pserver_labels()
                    },
                    "spec": {
                        "containers":[{
                            "name": self._get_pserver_job_name(),
                            "image": self._get_runtime_docker_image_name(),
                            "ports": self._get_pserver_container_ports(),
                            "env": self.get_env(),
                            "command": self._get_pserver_entrypoint()
                        }]
                    }
                }
            }
        }
