import os

from network_live.ftp import download_ftp_logs
from network_live.huawei_parser import parse_gsm_cells


def gsm_main(atoll_data):
    """
    Prepare Tele2 gsm cell data for Network Live.

    Args:
        atoll_data (dict): a dict of cell physical params

    Returns:
        list: a list of dicts containing the parameters for each GSM cell
    """
    download_ftp_logs('tele2_gsm')

    logs_path = 'logs/tele2'
    log_name = os.listdir(logs_path)[0]
    gsm_log_path = f'{logs_path}/{log_name}'

    return parse_gsm_cells(gsm_log_path, 'Tele2', atoll_data)
