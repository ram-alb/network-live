import os

import paramiko


def download_ftp_data(remote_path, local_path, ftp_type):
    """
    Download data from ftp server.

    Args:
        remote_path: string
        local_path: string
        ftp_type: string
    """
    if ftp_type == 'ftp_server':
        host = os.getenv('FTP_HOST')
        login = os.getenv('FTP_LOGIN')
        password = os.getenv('FTP_PASSWORD')
    elif ftp_type == 'oss':
        host = os.getenv('ASTOSS_HOST')
        login = os.getenv('ASTOSS_USER')
        password = os.getenv('ASTOSS_PASSWORD')

    with paramiko.Transport((host)) as transport:
        transport.connect(username=login, password=password)
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            sftp.get(remote_path, local_path)


def delete_old_logs(logs_path):
    """
    Delete previous logs.

    Args:
        logs_path: string
    """
    for log in os.listdir(logs_path):
        os.remove('{logs_path}/{log}'.format(logs_path=logs_path, log=log))


def download_oss_logs(technology):
    """
    Download logs from OSS.

    Args:
        technology: string
    """
    if technology == 'WCDMA':
        remote_path = '/home/anpusr/bcg_filters/export/oss_utrancells.xml'
    elif technology == 'GSM':
        remote_path = '/var/opt/ericsson/cnai/data/export/network_live_gsm_export.txt'
    log_name = os.path.basename(remote_path)
    logs_path = 'logs/oss'
    local_path = '{logs_path}/{log_name}'.format(logs_path=logs_path, log_name=log_name)
    delete_old_logs(logs_path)
    download_ftp_data(remote_path, local_path, 'oss')
    return local_path
