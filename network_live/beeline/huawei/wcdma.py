from network_live.ftp import download_bee250_huawei_xml
from network_live.huawei_parser import parse_huawei_wcdma_cells

import os

def wcdma_main(atoll_data):
    logs_path = 'logs/beeline'
    download_bee250_huawei_xml(logs_path)
    log_name = os.listdir(logs_path)[0]
    xml_path = f'{logs_path}/{log_name}'
    return parse_huawei_wcdma_cells(xml_path, 'Beeline', atoll_data)
