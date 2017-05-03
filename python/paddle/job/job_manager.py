import os
from paddle_job import PaddleJob
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.client import configuration

__all__ = ["JobManager"]
NAMESPACE = os.getenv("NAMESPACE", "default")

def init_api_client():
    service_host = os.getenv("KUBERNETES_SERVICE_HOST", None)
    ca_cert = os.getenv("CA_CERT", None)
    cert_file = os.getenv("CERT_FILE", None)
    key_file = os.getenv("KEY_FILE", None)
    if service_host and ca_cert and cert_file and key_file:
        # init kubernetes client with cert files
        configuration.host = service_host
        configuration.ssl_ca_cert = ca_cert
        configuration.cert_file = cert_file
        configuration.key_file = key_file
    elif service_host:
        # init kubernete client with service account
        config.load_incluster_config()
    else:
        # init kubernetes client with ~/.kube/config file
        config.load_kube_config()

class JobManager(object):
    def __init__(self, paddle_job):
        self.paddle_job = paddle_job
        init_api_client()

    def submit(self):
        #submit parameter server statefulset
        try:
            ret = client.AppsV1beta1Api().create_namespaced_stateful_set(
                namespace=NAMESPACE,
                body=self.paddle_job.new_pserver_job(),
                pretty=True)
        except ApiException, e:
            print "Exception when submit pserver job: %s " % e
            return False

        #submit trainer job
        try:
            ret = client.BatchV1Api().create_namespaced_job(
                namespace=NAMESPACE,
                body=self.paddle_job.new_trainer_job(),
                pretty=True)
        except ApiException, e:
            print "Exception when submit trainer job: %s" % e
            return False
        return True
