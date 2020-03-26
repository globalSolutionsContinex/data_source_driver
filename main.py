import logging
import sys
import threading
import uuid
import datetime
from infrastructure import config, log
import Manager.controller as retailer_controller
from Descriptor import master

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

# allow track all `logging` instances
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


logger = log.get_logger("main")
jobs_running = {}


def get_config():
    config_path = sys.argv[1]
    return config.get_config(config_path)


def schedule_jobs(configuration):

    # Configuration
    s3_config = configuration['s3']
    s3_thor_config = configuration['s3_thor']
    monitor_db_config = configuration['monitor_db']
    stage = configuration['stage']

    # create Data flows
    for data_flow in master.data_flows:
        flow = master.data_flows[data_flow]
        logger.info("*** Init {} Flow ***".format(data_flow))
        update_flow = retailer_controller.UpdateRetailer(flow['descriptor'],
                                                         stage, s3_config, s3_thor_config, monitor_db_config)
        logger.info("*** {} Schedule run every {} seconds ***".format(data_flow, flow['run_every_seconds']))
        create_interval_job(seconds=flow['run_every_seconds'], job=update_flow, initial_hour=flow['initial_hour'], final_hour=flow['final_hour'])


def run_job(job, process, initial_hour, final_hour):
    now = datetime.datetime.now()
    hour = now.hour
    if initial_hour <= hour <= final_hour:
        if not jobs_running[process]["is_running"]:
            try:
                jobs_running[process]["is_running"] = True
                job.logger.info("starting job")
                job.run()
                job.logger.info("job finished")
                jobs_running[process]["is_running"] = False
            except Exception as ex:
                job.logger.info("job finished with errors: " + str(ex))
                logger.info(str(ex))
                jobs_running[process]["is_running"] = False
        else:
            job.logger.info("is_running")
    else:
        job.logger.info("The job will run between " + str(initial_hour) + " and " + str(final_hour) + " The actual hour is: " + str(hour))


def create_interval_job(seconds, job, initial_hour, final_hour):
    process = uuid.uuid4().hex
    interval = set_interval(seconds, run_job, *[job, process, initial_hour, final_hour])
    jobs_running[str(process)] = {"is_running": False, "interval": interval}


def set_interval(sec, func, *args):
    # each interval run in a different thread
    def func_wrapper():
        func(*args)
        set_interval(sec, func, *args)

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t  


if __name__ == "__main__":
    # load configuration
    config = get_config()
    logger.info("------------------------------------------------------------------")
    logger.info("starting data source flow")
    logger.info("------------------------------------------------------------------")
    schedule_jobs(config)
