import os
from network_live.ftp import download_ftp_logs
from network_live.huawei_parser import parse_huawei_wcdma_cells


def wcdma_main(atoll_data):
    download_ftp_logs('tele2_wcdma')

    logs_path = 'logs/tele2'
    log_name = os.listdir(logs_path)[0]
    wcdma_log_path = f'{logs_path}/{log_name}'

    cells = parse_huawei_wcdma_cells(wcdma_log_path, 'Tele2', atoll_data)
    return cells
