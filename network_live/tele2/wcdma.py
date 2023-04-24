import os

from network_live.ftp import download_ftp_logs
from network_live.huawei_parser import parse_huawei_wcdma_cells


def wcdma_main(atoll_data):
    """
    Prepare Tele2 wcdma cell data for Network Live.

    Args:
        atoll_data (dict): a dict of cell physical params

    Returns:
        list: a list of dicts containing the parameters for each WCDMA cell
    """
    download_ftp_logs('tele2_wcdma')

    logs_path = 'logs/tele2'
    log_name = os.listdir(logs_path)[0]
    wcdma_log_path = f'{logs_path}/{log_name}'

    return parse_huawei_wcdma_cells(wcdma_log_path, 'Tele2', atoll_data)
