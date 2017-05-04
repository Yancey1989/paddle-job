import os
from job_manager import JobManager
__all__=["dist_train"]

def get_parameter(parameter, env_parameter):
    if parameter:
        return parameter
    else:
        if os.getenv(env_parameter, None):
            return os.getenv(env_parameter)
    return ""


def dist_train(trainer,
               reader,
               num_passes=1,
               event_handler=None,
               feeding=None,
               paddle_job=None):
    if os.getenv("PADDLE_ON_CLOUD", "NO") == "NO":
        # if PADDLE_ON_CLOUD=NO, submit the distributed training job
        job_manager = JobManager(paddle_job)
        if not job_manager.submit():
            print "submit paddle job failed."
        else:
            print "submit paddle job successed."
    else:
        trainer.train(
            reader=reader,
            num_passes=num_passes,
            event_handler=event_handler,
            feeding=feeding)
