import os
from datetime import date

from defusedxml import ElementTree
from network_live.beeline.unwanted_cells import unwanted_lte_cells
from network_live.ftp import download_ftp_logs
from network_live.physical_params import add_physical_params


def make_tag(tag):
    """
    Make tag name with namespace.

    Args:
        tag: string

    Returns:
        string
    """
    ns = '{http://www.huawei.com/specs/bsc6000_nrm_forSyn_collapse_1.0.0}'
    return f'{ns}{tag}'


def parse_tag_text(tag, parent):
    """
    Parse tags text content.

    Args:
        tag: string
        parent: string

    Returns:
        string
    """
    attributes = parent.find(make_tag('attributes'))
    return attributes.find(make_tag(tag)).text


def parse_qrxlevmin(root):
    """
    Parse qrxlevmin for all cells.

    Args:
        root: root object

    Returns:
        dict
    """
    qrxlevmin_data = {}
    for element in root.iter(make_tag('CellSel')):
        cell_id = parse_tag_text('LocalCellId', element)
        qrxlevmin = parse_tag_text('QRxLevMin', element)
        qrxlevmin_data[cell_id] = int(qrxlevmin) * 2
    return qrxlevmin_data


def parse_tac(root, sharing):
    """
    Parse Kcell tac.

    Args:
        root: root object
        sharing: string

    Returns:
        string
    """
    for element in root.iter(make_tag('CnOperatorTa')):
        if sharing == 'moran':
            tracking_area_id = parse_tag_text('TrackingAreaId', element)
            if tracking_area_id == '1':
                return parse_tag_text('Tac', element)
        else:
            return parse_tag_text('Tac', element)


def parse_ip(root):
    """
    Parse S1 Kcell ip address.

    Args:
        root: root object

    Returns:
        string
    """
    for element in root.iter(make_tag('DEVIP')):
        user_label = parse_tag_text('USERLABEL', element)
        if user_label == 'S1 Kcell':
            return parse_tag_text('IP', element)


def parse_enodeb_id(root):
    """
    Parse enodeb id.

    Args:
        root: root object

    Returns:
        string
    """
    enodeb_id = ''
    for element in root.iter(make_tag('eNodeBFunction')):
        enodeb_id = parse_tag_text('eNodeBId', element)
    return enodeb_id


def parse_site_name(root):
    """
    Parse site name.

    Args:
        root: root object

    Returns:
        string
    """
    site_name = ''
    for element in root.iter(make_tag('NE')):
        site_name = parse_tag_text('NENAME', element)
    return site_name


def parse_huawei_xml(xml_path, sharing, atoll_data):
    """
    Parse xml file.

    Args:
        xml_path: string
        sharing: string
        atoll_data: dict

    Returns:
        dict
    """
    eci_factor = 256
    root = ElementTree.parse(xml_path).getroot()

    qrxlevmin_data = parse_qrxlevmin(root)
    enodeb_id = parse_enodeb_id(root)
    eutrancells = []
    moran_min_cell_id, moran_max_cell_id = (100, 130)
    moran_cellid_range = list(range(moran_min_cell_id, moran_max_cell_id))

    mocn_min_cell_id, mocn_max_cell_id = (0, 100)
    mocn_cellid_range = list(range(mocn_min_cell_id, mocn_max_cell_id))

    if sharing == 'moran':
        cellid_range = moran_cellid_range
    else:
        cellid_range = mocn_cellid_range

    for element in root.iter(make_tag('Cell')):
        cell = {
            'oss': 'Beeline Huawei',
            'subnetwork': 'Beeline',
            'vendor': 'Huawei',
            'insert_date': date.today(),
            'cellRange': None,
            'primaryPlmnReserved': None,
        }
        cell_id = parse_tag_text('LocalCellId', element)

        if int(cell_id) in cellid_range:
            if parse_tag_text('CellActiveState', element) == '1':
                cell_state = 'UNLOCKED'
            else:
                cell_state = 'LOCKED'

            cell_name = parse_tag_text('CellName', element)
            if cell_name in unwanted_lte_cells:
                continue
            cell['cell_name'] = cell_name
            cell['cellId'] = cell_id
            cell['earfcndl'] = parse_tag_text('DlEarfcn', element)
            cell['administrativeState'] = cell_state
            cell['rachRootSequence'] = parse_tag_text(
                'RootSequenceIdx',
                element,
            )
            cell['physicalLayerCellId'] = parse_tag_text('PhyCellId', element)
            cell['qRxLevMin'] = qrxlevmin_data[cell_id]
            cell['tac'] = parse_tac(root, sharing)
            cell['ip_address'] = parse_ip(root)
            cell['enodeb_id'] = enodeb_id
            cell['site_name'] = parse_site_name(root)
            cell['eci'] = int(enodeb_id) * eci_factor + int(cell_id)

            eutrancells.append(
                add_physical_params(atoll_data, cell),
            )

    return eutrancells


def parse_lte_huawei(logs_path, sharing, atoll_data):
    """
    Parse Beeline Huawei xml logs.

    Args:
        logs_path: string
        sharing: string
        atoll_data: sict

    Returns:
        list of dicts
    """
    cell_data = []
    for log in os.listdir(logs_path):
        xml_path = '{logs_path}/{log}'.format(logs_path=logs_path, log=log)
        cell_data += parse_huawei_xml(xml_path, sharing, atoll_data)

    return cell_data


def lte_main(atoll_data):
    """
    Prepare shared by Beeline Huawei lte cell data for Network Live.

    Args:
        atoll_data (dict): a dict of cell physical params

    Returns:
        list: a list of dicts containing the parameters for each LTE cell
    """
    logs_path = 'logs/beeline'

    download_ftp_logs('beeline_huawei')
    cells = parse_lte_huawei(logs_path, 'moran', atoll_data)

    download_ftp_logs('beeline_huawei_mocn')
    cells += parse_lte_huawei(logs_path, 'mocn', atoll_data)

    return cells
