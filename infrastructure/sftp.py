class SftpClient(object):

    def __init__(self, client, sftp):
        self.client = client
        self.sftp = sftp

    def close(self):
        self.sftp.close()
        self.client.close()
