import csv
from datetime import date
import re

from network_live.ftp import download_ftp_logs
from network_live.physical_params import add_physical_params
from point_in_region import find_region_by_coordinates


def convert_string_to_num(string_value):
    """
    Convert string value to number.

    Args:
        string_value: string

    Returns:
        number
    """
    try:
        num_value = round(float(string_value))
    except ValueError:
        num_value = None

    return num_value


def str_to_int(value):
    num = float(value)
    return int(num)


def parse_tx_rx(mimo):
    """Parse a string of the format '2T2R' and return a tuple with the counts of Tx and Rx."""
    if mimo is None:
        return None, None

    match = re.match(r'(\d+)T(\d+)R', mimo)
    if not match:
        return None, None

    t_count, r_count = map(int, match.groups())
    return t_count, r_count


def parse_lte(log_path, atoll_data):
    """
    Parse lte cells shared by Tele2.

    Args:
        log_path: string
        atoll_data: dict

    Returns:
        list of dicts
    """
    lte_cells = []
    with open(log_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row['Local tracking area ID'] not in {'2', '2.0'}:
                continue

            if row['Cell admin state'] == 'CELL_UNBLOCK':
                cell_state = 'UNLOCKED'
            else:
                cell_state = 'LOCKED'

            try:
                tx_num, rx_num = parse_tx_rx(row['Cell transmission and reception mode'])
            except KeyError:
                tx_num, rx_num = None, None

            lte_cell = {
                'oss': 'Tele2',
                'subnetwork': 'Tele2',
                'ip_address': None,
                'vendor': 'Huawei',
                'insert_date': date.today(),
            }
            lte_cell['enodeb_id'] = convert_string_to_num(row['eNodeB Id'])
            lte_cell['site_name'] = row['NENAME']
            lte_cell['cell_name'] = row['Cell Name']
            lte_cell['tac'] = row['Tracking area code']
            lte_cell['cellId'] = row['Cell ID']
            lte_cell['eci'] = convert_string_to_num(row['eCI'])
            lte_cell['earfcndl'] = convert_string_to_num(row['Downlink EARFCN'])
            lte_cell['qRxLevMin'] = str_to_int(
                row['CELLSEL Minimum required RX level(2dBm)'],
            ) * 2
            lte_cell['administrativeState'] = cell_state
            lte_cell['rachRootSequence'] = convert_string_to_num(
                row['Root sequence index'],
            )
            lte_cell['physicalLayerCellId'] = row['Physical cell ID']
            lte_cell['cellRange'] = None
            lte_cell['primaryPlmnReserved'] = None
            lte_cell['txNumber'] = tx_num
            lte_cell['rxNumber'] = rx_num

            cell_with_phys_params = add_physical_params(atoll_data, lte_cell)
            try:
                cell_with_phys_params['region'] = find_region_by_coordinates(
                    (cell_with_phys_params['longitude'], cell_with_phys_params['latitude']),
                )
            except TypeError:
                cell_with_phys_params['region'] = None

            lte_cells.append(cell_with_phys_params)
    return lte_cells


def lte_main(atoll_data):
    """
    Prepare Tele2 lte cell data for Network Live.

    Args:
        atoll_data (dict): a dict of cell physical params

    Returns:
        list: a list of dicts containing the parameters for each LTE cell
    """
    log_path = 'logs/tele2/tele2_lte_log.csv'

    download_ftp_logs('tele2_lte')
    cells = parse_lte(log_path, atoll_data)

    download_ftp_logs('tele2_lte_250')
    cells += parse_lte(log_path, atoll_data)

    return cells
