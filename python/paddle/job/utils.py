import os
from job_manager import JobManager
__all__=["dist_train"]

def get_parameter(parameter, env_parameter, default):
    if parameter:
        return parameter
    else:
        if os.getenv(env_parameter, None):
            return os.getenv(env_parameter)
        else:
            return default

def dist_train(trainer,
               paddle_job):
    if os.getenv("RUNNING_ON_CLOUD", "NO") == "NO":
        job_manager = JobManager(paddle_job)
        if not job_manager.submit():
            print "submit Paddle Job failed."
        else:
            print "submit Paddle Job successed."
    else:
        trainer()
