from infrastructure import files, log
import DataSource.ftp as ftp
import DataSource.s3 as s3


class Connect:

    def __init__(self, descriptor, s3_client, stage):
        self.s3_client = s3_client  # type:s3.S3Client
        self.stage = stage
        self.data_descriptor = descriptor.data_descriptor
        self.logger = log.get_logger(self.data_descriptor['name'])
        self.channel_descriptor = descriptor.channel_descriptor
        self.logger.info('init channel_controller')
        # data sources type
        self.FTP = 'ftp'
        self.FTP_TLS = 'ftp_tls'
        self.SFTP_TUNNEL = 'sftp_tunnel'
        self.SFTP = 'sftp'
        self.S3 = 's3'
        # parameters
        self.CONNECTION = 'connection'
        self.HOST = 'host'
        self.USER = 'user'
        self.PORT = 'port'
        self.PASSWORD = 'password'
        self.INFO_TYPE = 'info_type'
        self.BACKUP = 'backup'
        self.PRIVATE_FILE_KEY = 'private_key_file'
        self.PROCESSED_PATH = 'processed_path'
        self.DECRYPT_KEYS = 'decrypt_key_paths'
        self.DIR_PATH = 'dir_path'
        self.IS_ENCRYPTED = 'is_encrypted'
        self.IP_TUNNEL = 'ip_tunnel'
        self.PORT_TUNNEL = 'port_tunnel'
        self.BANNER_TIMEOUT = 'banner_timeout'
        self.METHOD = 'method'
        self.NAME = 'name'
        self.SSH_HOST = 'ssh_host'
        self.SSH_USERNAME = 'ssh_username'
        self.SSH_PRIVATE_KEY_FILE = 'ssh_private_key_file'
        self.MAX_FILES_TO_RUN = 5
        self.ftp_lib = ftp.FtpCommon()

    def get_files(self):
        if self.channel_descriptor[self.CONNECTION] == self.FTP:
            return self.get_file_ftp(is_tls=False)
        if self.channel_descriptor[self.CONNECTION] == self.FTP_TLS:
            return self.get_file_ftp(is_tls=True)
        if self.channel_descriptor[self.CONNECTION] == self.SFTP_TUNNEL:
            return self.get_file_sftp_tunnel()
        if self.channel_descriptor[self.CONNECTION] == self.SFTP:
            return self.get_file_sftp()
        if self.channel_descriptor[self.CONNECTION] == self.S3:
            return self.get_file_s3()
        return [None, None, None]

    def get_file_s3(self):
        local_directory = f'{self.data_descriptor[self.NAME]}/'
        self.logger.info("extracting file...")
        today_files = self.s3_client.get_pending_files(local_directory, self.data_descriptor[self.INFO_TYPE])
        pending_files = self.process_file(today_files, local_directory,
                                          self.s3_client.download_file, self.s3_client.client, self.s3_client.move_file)
        s3_path = "{}{}".format(local_directory, self.data_descriptor[self.METHOD])
        return [pending_files, s3_path]

    def get_file_ftp(self, is_tls):
        local_directory = f'{self.data_descriptor[self.NAME]}/'
        host = self.channel_descriptor[self.HOST]
        user = self.channel_descriptor[self.USER]
        password = self.channel_descriptor[self.PASSWORD]
        self.logger.info("connecting ftp...")
        ftp = self.ftp_lib.get_ftp_tls(host, user, password) if is_tls else self.ftp_lib.get_ftp(host, user, password)
        ftp.cwd(self.channel_descriptor[self.DIR_PATH])
        self.logger.info("extracting file...")
        today_files = self.ftp_lib.get_ftp_today_files(ftp, self.data_descriptor)
        pending_files = self.process_file(today_files, local_directory, self.ftp_lib.download_ftp_file, ftp, self.ftp_lib.move_file)
        ftp.close()
        s3_path = "{}{}".format(local_directory, self.data_descriptor[self.METHOD])
        return [pending_files, s3_path]

    def get_file_sftp(self):
        local_directory = f'{self.data_descriptor[self.NAME]}/'
        host = self.channel_descriptor[self.HOST]
        user = self.channel_descriptor[self.USER]
        port = self.channel_descriptor[self.PORT]
        password = self.channel_descriptor[self.PASSWORD]
        dir_path = self.channel_descriptor[self.DIR_PATH]
        private_file_key = self.channel_descriptor[self.PRIVATE_FILE_KEY]
        self.logger.info("connecting self.ftp_lib...")
        sftp_instance = self.ftp_lib.get_sftp_client(host, port, user, password, key_filename=private_file_key)
        sftp_client = sftp_instance.sftp
        sftp_client.chdir(dir_path)
        self.logger.info("extracting file...")
        today_files = self.ftp_lib.get_sftp_today_files(sftp_client, self.data_descriptor)
        pending_files = self.process_file(today_files, local_directory, self.ftp_lib.download_sftp_file, sftp_client, self.ftp_lib.move_file,
                                          is_encrypted=self.channel_descriptor[self.IS_ENCRYPTED])
        sftp_instance.close()
        s3_path = "{}{}".format(local_directory, self.data_descriptor[self.METHOD])
        return[pending_files, s3_path]

    def process_file(self, today_files, local_directory, download_file_method, client, move_func, is_encrypted=False):
        self.logger.info("today file... count " + str(len(today_files)))
        pending_files = []
        count_files = 1
        for latest_file_name in today_files:
            try:
                latest_file_name = str(latest_file_name).replace('./', '')
                self.logger.info("latest_file_name... " + str(latest_file_name))
                self.logger.info("downloading file...")
                files.create_directory_if_not_exists(local_directory)
                latest_file_path = download_file_method(client, latest_file_name, local_directory)
                if is_encrypted:
                    self.logger.info("decrypting...")
                    decrypted_path = latest_file_path
                else:
                    decrypted_path = latest_file_path
                if self.channel_descriptor[self.BACKUP]:
                    self.logger.info("uploading file s3...")
                    s3_file = self.upload_file(decrypted_path, local_directory)
                    self.logger.info("uploaded file s3..." + str(s3_file))
                else:
                    s3_file = decrypted_path
                self.logger.info("latest_file_path: " + str(decrypted_path))
                pending_files.append([decrypted_path, s3_file, latest_file_name])
                # for security only in production is possible move files to processed path
                if self.stage == 'production':
                    self.logger.info("moving {} to {}...".format(latest_file_path,self.channel_descriptor[self.PROCESSED_PATH]))
                    self.move_file(move_func, client, latest_file_name, self.channel_descriptor[self.PROCESSED_PATH])
                if count_files >= self.MAX_FILES_TO_RUN:
                    break
                count_files += 1
            except Exception as ex:
                self.logger.info("Error " + str(ex))

        return pending_files

    @staticmethod
    def move_file(move_func, client, file_path, destiny_path):
        move_func(client, file_path, destiny_path)

    def upload_file(self, file_path, folder_name):
        folder_name = folder_name.replace("/", "")
        return self.s3_client.upload_file(folder_name, file_path)

