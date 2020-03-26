from ftplib import FTP_TLS
from ftplib import FTP
from infrastructure.sftp import SftpClient
from os import path
import paramiko


class FtpCommon:

    @staticmethod
    def get_ftp(host, username, password):
        ftp = FTP(host)
        resp = ftp.login(username, password)
        return ftp

    @staticmethod
    def get_ftp_tls(host, username, password):
        ftp_tls = FTP_TLS(host)
        ftp_tls.login(username, password)
        ftp_tls.prot_p()
        return ftp_tls

    @staticmethod
    def get_sftp_client(host, port, username, password, key_filename=None, banner_timeout=1000):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            banner_timeout=banner_timeout,
            key_filename=key_filename
        )
        sftp_client = client.open_sftp()
        return SftpClient(client, sftp_client)

    @staticmethod
    def get_file_datetime(file_name):
        base = path.basename(file_name)
        return base

    # Get today files using name pattern matching.
    @staticmethod
    def get_ftp_today_files(ftp_client, retailer):
        today_pattern = "{}*".format(retailer['name_pattern'])
        today_files = ftp_client.nlst(today_pattern)
        return today_files

    @staticmethod
    def get_sftp_today_files(sftp_client, retailer):
        today_pattern = "{0}".format(retailer['name_pattern'])
        listdir = sftp_client.listdir()
        today_files = []
        for item in listdir:
            if today_pattern in item:
                today_files.append(item)
        return today_files

    @staticmethod
    def download_ftp_file(ftp_client, file_name, local_directory):
        file_path = local_directory + file_name
        a_file = open(file_path, 'wb')
        ftp_client.retrbinary('RETR %s' % file_name, a_file.write)
        return file_path

    @staticmethod
    def download_sftp_file(sftp_client, file_name, local_directory):
        file_path = local_directory + file_name
        sftp_client.get(file_name, file_path)
        return file_path

    @staticmethod
    def move_file(sftp_client, file_path, dest_dir):
        file_path_to = dest_dir + file_path
        sftp_client.rename(file_path, file_path_to)
