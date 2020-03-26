import uuid
import json
import DataSource.controller as dataSource
import DataSource.s3 as s3
import Manager.get_info as gi
from infrastructure import log, files


class UpdateRetailer:

    def __init__(self, descriptor, stage, s3_config, s3_thor_config):
        self.descriptor = descriptor
        self.s3_config = s3_config
        self.s3_thor_config = s3_thor_config
        self.logger = log.get_logger(self.descriptor.data_descriptor['name'])
        self.s3_client = None
        self.s3_thor_client = None
        self.channel_controller = None
        self.get_info = None
        self.get_dictionary = None
        self.monitor_client = None
        self.process_uuid = None
        self.rds_controller = None
        self.count_data_sent = 0
        self.stage = stage['env']
        self.obj_fixed_prices = {}

    def open_connections(self):

        try:
            self.logger.info("init controller")
            self.logger.info("init s3...")
            self.s3_client = s3.S3Client(self.s3_config)
            self.s3_thor_client = s3.S3Client(self.s3_thor_config)
            self.logger.info("init redis...")
            self.logger.info("init channel_controller...")
            self.rds_controller = dataSource.Connect(self.descriptor, self.s3_client, self.stage)
            self.logger.info("init get_info...")
            self.get_info = gi.FileInfoExtractor(self.descriptor)
            self.logger.info("init monitor...")
            self.process_uuid = uuid.uuid4().hex
            return True
        except Exception as ex:
            self.logger.exception(ex)
            return False

    def run(self):
        if self.open_connections():
            try:
                self.logger.info("starting proccess..." + self.process_uuid)
                self.logger.info("Monitor update: Start of a new process...")
                pending_files, path = self.rds_controller.get_files()
                for file_path, s3_path, file_name in pending_files:
                    try:
                        self.process_uuid = uuid.uuid4().hex
                        if file_path:
                            self.logger.info("generating list of data...")
                            list_data, list_data_errors = self.process_file(file_path)
                            self.count_data_sent = len(list_data)
                            data = json.dumps(list_data).encode('latin-1')
                            data_error = json.dumps(list_data_errors).encode('latin-1')
                            self.logger.info("uploading json to s3...")
                            file_name = files.get_file_name(file_name)
                            self.s3_thor_client.upload_json(folder_name=path, file_name="{}.json".format(file_name),
                                                       data=data)
                            if len(list_data_errors) > 0:
                                self.s3_thor_client.upload_json(folder_name="{}_error".format(path),
                                                           file_name="{}_error.json".format(file_name), data=data_error)
                            self.logger.info("deleting local file...")
                            # Remove local files
                            files.remove_file(file_path)
                    except Exception as ex:
                        self.logger.info(str(ex))
                self.logger.info("closing connections...")
            except Exception as ex:
                self.logger.exception(ex)
            finally:
                self.logger.info("Done...")

    # process the file and obtain an object with a report of number of records approved and with errors
    def process_file(self, file_path):
        try:
            list_data, list_data_errors = self.get_info.process_file(file_path)
            self.logger.info("data: " + str(len(list_data)))
            self.logger.info("data with extracting errors: " + str(len(list_data_errors)))
            return [list_data, list_data_errors]
        except Exception as ex:
            self.logger.exception("error processing file: " + str(ex))
            return [[], ["Error to process file ", file_path, str(ex)]]










