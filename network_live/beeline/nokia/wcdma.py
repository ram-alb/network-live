from datetime import date

from defusedxml import ElementTree
from network_live.beeline.nokia.utils import (
    get_xml_path,
    make_tag,
    parse_cell_parameter,
    parse_nodes,
    parse_sites,
)
from network_live.ftp import download_ftp_logs
from network_live.physical_params import add_physical_params


def parse_nokia_wcdma_cells(logs_path, atoll_data):
    """
    Parse WCDMA cells from Nokia xml file.

    Args:
        logs_path: string
        atoll_data: dict

    Returns:
        list of dicts
    """
    uarfcnul = {
        '2965': 2740,
        '2999': 2774,
        '10562': 9612,
        '10587': 9637,
        '10662': 9712,
        '10687': 9737,
        '10712': 9762,
        '10737': 9787,
    }
    root = ElementTree.parse(get_xml_path(logs_path, 'UMTS')).getroot()
    sites = parse_sites(root, 'WCDMA')

    wcdma_cells = []
    for cell_tag in root.iter(make_tag('managedObject')):
        if cell_tag.get('class') != 'WCEL':
            continue
        site_id, rnc_name, rnc_id = parse_nodes(cell_tag)
        if parse_cell_parameter(cell_tag, 'AdminCellState') == '1':
            cell_state = 'UNLOCKED'
        else:
            cell_state = 'LOCKED'
        uarfcndl = parse_cell_parameter(cell_tag, 'UARFCN')
        cell_id = parse_cell_parameter(cell_tag, 'CId')
        cell = {
            'operator': 'Beeline',
            'oss': 'Beeline Nokia',
            'rnc_id': rnc_id,
            'rnc_name': rnc_name,
            'site_name': sites[site_id],
            'cell_name': parse_cell_parameter(cell_tag, 'name'),
            'cId': cell_id,
            'localCellId': cell_id,
            'uarfcnDl': uarfcndl,
            'uarfcnUl': uarfcnul[uarfcndl],
            'primaryScramblingCode': parse_cell_parameter(
                cell_tag,
                'PriScrCode',
            ),
            'LocationArea': parse_cell_parameter(cell_tag, 'LAC'),
            'RoutingArea': parse_cell_parameter(cell_tag, 'RAC'),
            'ServiceArea': parse_cell_parameter(cell_tag, 'SAC'),
            'Ura': None,
            'primaryCpichPower': parse_cell_parameter(
                cell_tag,
                'PtxPrimaryCPICH',
            ),
            'maximumTransmissionPower': parse_cell_parameter(
                cell_tag,
                'PtxCellMax',
            ),
            'IubLink': None,
            'MocnCellProfile': None,
            'administrativeState': cell_state,
            'ip_address': None,
            'vendor': 'Nokia',
            'insert_date': date.today(),
            'qRxLevMin': int(parse_cell_parameter(cell_tag, 'QrxlevMin')) * 2,
            'qQualMin': int(parse_cell_parameter(cell_tag, 'QqualMin')) * 2,
        }
        wcdma_cells.append(
            add_physical_params(atoll_data, cell),
        )
    return wcdma_cells


def wcdma_main(atoll_data):
    """
    Prepare shared by Beeline Nokia wcdma cell data for Network Live.

    Args:
        atoll_data (dict): a dict of cell physical params

    Returns:
        list: a list of dicts containing the parameters for each WCDMA cell
    """
    logs_path = 'logs/beeline'

    download_ftp_logs('beeline_nokia_250', is_unzip=False)
    cells = parse_nokia_wcdma_cells(logs_path, atoll_data)

    download_ftp_logs('beeline_nokia_250_Kok', is_unzip=False)
    cells += parse_nokia_wcdma_cells(logs_path, atoll_data)

    download_ftp_logs('beeline_nokia_gu')
    cells += parse_nokia_wcdma_cells(logs_path, atoll_data)
    return cells
