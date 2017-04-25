from job.paddle_job import PaddleJob
from kubernetes import client, config

config.load_kube_config()
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

v1beta1api = client.AppsV1beta1Api()
ret = v1beta1api.create_namespaced_stateful_set(namespace="yanxu", body=paddle_job.new_pserver_job())
print ret
batchv1api = client.BatchV1Api()
ret = batchv1api.create_namespaced_job(namespace="yanxu", body=paddle_job.new_trainer_job())
print ret
