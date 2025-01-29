import os
from network_live.ftp import download_bee250_zte_xml
from dotenv import load_dotenv
from network_live.beeline.zte.parsing import parse_gsm_parameters, parse_wcdma_parameters, parce_lte_parameters
load_dotenv()


def beeline_zte_main(technology=None):
    logs_path = 'logs/beeline/zte'
    download_bee250_zte_xml(logs_path)
    log_name = next((f for f in os.listdir(logs_path) if f.startswith('UMEID_MRNC')), None)
    xml_path = f'{logs_path}/{log_name}'
    lte_folder = None
    plat_folder = None

    for folder in os.listdir(logs_path):
        if folder.startswith('lte-'):
            lte_folder = os.path.join(logs_path, folder)
        elif folder.startswith('plat-'):
            plat_folder = os.path.join(logs_path, folder)
    
    lte_file = os.path.join(lte_folder, 'CUEUtranCellFDDLTE.csv')
    plat_file = os.path.join(plat_folder, 'Ip.csv')
    
    
    if technology == 'GSM':
        cell_2g = parse_gsm_parameters(xml_path)
        return cell_2g
    elif technology == 'WCDMA':
        cell_3g = parse_wcdma_parameters(xml_path)
        return cell_3g
    elif technology == 'LTE':
        cell_4g = parce_lte_parameters(lte_file, plat_file)
        return cell_4g
    else:
        return cell_2g, cell_3g, cell_4g

