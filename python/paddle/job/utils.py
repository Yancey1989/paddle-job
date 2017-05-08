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

def dist_train(trainer_func,
               reader,
               num_passes=1,
               event_handler=None,
               feeding=None,
               paddle_job=None):
    if os.getenv("RUNNING_ON_CLOUD", "NO") == "NO":
        job_manager = JobManager(paddle_job)
        if not job_manager.submit():
            print "submit paddle job failed."
        else:
            print "submit paddle job successed."
    else:
	trainer = trainer_func()
        trainer.train(
            reader=reader,
            num_passes=num_passes,
            event_handler=event_handler,
            feeding=feeding)
