import re
from datetime import date

from defusedxml import ElementTree
from network_live.enm.enm_cli import EnmCli
from network_live.enm.utils import parse_bbu_ips, parse_node_parameter
from network_live.ftp import download_oss_logs
from network_live.oss.oss_ssh import collect_oss_logs
from network_live.physical_params import add_physical_params

es_ns = '{EricssonSpecificAttributes.18.29.xsd}'
xn_ns = '{genericNrm.xsd}'
un_ns = '{utranNrm.xsd}'
id_attr = 'id'


def make_tag(tag, namespace):
    """
    Make tag name with namespace.

    Args:
        tag: string
        namespace: stirng

    Returns:
        string
    """
    return '{namespace}{tag}'.format(namespace=namespace, tag=tag)


def parse_rbs_ip(me_context_tag):
    """
    Parse RBS ip address.

    Args:
        me_context_tag: xml tag object

    Returns:
        string
    """
    ip_address = 0
    for data_tag in me_context_tag.iter(make_tag('vsdatacontainer', xn_ns)):
        container_id = data_tag.get(id_attr)
        if 'oam' not in container_id.lower():
            continue
        for oam_ip_tag in data_tag.iter(make_tag('usedAddress', es_ns)):
            ip_address = oam_ip_tag.text.split('/')[0]

    if ip_address == 0:
        for ip_tag in me_context_tag.iter(make_tag('ipAddress', es_ns)):
            ip_address = ip_tag.text
    if ip_address == 0:
        ip_address = None
    return ip_address


def parse_rbs_id(me_context_tag):
    """
    Parse rbsId for RBS nodes.

    Args:
        me_context_tag: xml tag object

    Returns:
        string
    """
    rbs_id = 0
    for iub_rbs_id_tag in me_context_tag.iter(make_tag('rbsIubId', es_ns)):
        rbs_id = iub_rbs_id_tag.text
    if rbs_id == 0:
        for rbs_id_tag in me_context_tag.iter(make_tag('rbsId', es_ns)):
            rbs_id = rbs_id_tag.text
    return rbs_id


def parse_rbs_data(root, enm_sites, enm_ips):
    """
    Parse rbsId and ip address for sites whick configured on oss ass Wrat nodes.

    Args:
        root: xml root object
        enm_sites: dict
        enm_ips: dict

    Returns:
        dict
    """
    rbs_data = {}
    for me_context_tag in root.iter(make_tag('MeContext', xn_ns)):
        me_tag_id = me_context_tag.get(id_attr)
        if 'RNC' in me_tag_id:
            continue
        ip_address = parse_rbs_ip(me_context_tag)
        rbs_id = parse_rbs_id(me_context_tag)
        rbs_data[rbs_id] = {
            'site_name': me_tag_id,
            'ip_address': ip_address,
        }

    for site_name, enm_rbs_id in enm_sites.items():
        ip_address = enm_ips[site_name]
        rbs_data[enm_rbs_id] = {
            'site_name': site_name,
            'ip_address': ip_address,
        }

    return rbs_data


def parse_iublink_data(root):
    """
    Parse rbsId for every IubLink.

    Args:
        root: xml root object

    Returns:
        dict
    """
    rbs_ids = {}
    for iub_link_tag in root.iter(make_tag('IubLink', un_ns)):
        iub_link = iub_link_tag.get(id_attr)
        for rbs_id_tag in iub_link_tag.iter(make_tag('rbsId', es_ns)):
            rbs_id = rbs_id_tag.text
            rbs_ids[iub_link] = rbs_id
    return rbs_ids


def parse_attributes_value(tag, attr):
    """
    Get value of parameters inside attributes.

    Args:
        tag: xml tag object
        attr: string

    Returns:
        string
    """
    attributes = tag.find(make_tag('attributes', un_ns))
    return attributes.find(make_tag(attr, un_ns)).text


def parse_mocn_value(mocn_tag_text):
    """
    Parse mocnCellProfile parameter from tag text.

    Args:
        mocn_tag_text (str): a text of tag

    Returns:
        str: mocnCellProfile parameter value
    """
    mocn_value_index = -1
    mo = re.search('vsDataMocnCellProfile=.*', mocn_tag_text).group()
    return mo.split('=')[mocn_value_index]


def parse_data_utran_cell(utran_cell_tag):
    """
    Parse mocnCellProfile and administrativeState parameters.

    Args:
        utran_cell_tag: xml tag object

    Returns:
        tuple
    """
    mocn_cell_profile = ''
    administrative_state = ''
    qrxlevmin = ''
    qqualmin = ''
    for mocn_tag in utran_cell_tag.iter(make_tag('mocnCellProfileRef', es_ns)):
        try:
            mocn_cell_profile = parse_mocn_value(mocn_tag.text)
        except TypeError:
            mocn_cell_profile = mocn_tag.text

    for st_tag in utran_cell_tag.iter(make_tag('administrativeState', es_ns)):
        if st_tag.text == '1':
            administrative_state = 'UNLOCKED'
        else:
            administrative_state = 'LOCKED'

    for qrxlev_tag in utran_cell_tag.iter(make_tag('qRxLevMin', es_ns)):
        qrxlevmin = qrxlev_tag.text

    for qqual_tag in utran_cell_tag.iter(make_tag('qQualMin', es_ns)):
        qqualmin = qqual_tag.text

    return (mocn_cell_profile, administrative_state, qrxlevmin, qqualmin)


def get_site_name(sites, rbs_id):
    """
    Get site name from sites pool by rbs_id.

    Args:
        sites: dict
        rbs_id: string

    Returns:
        string
    """
    try:
        site_name = sites[rbs_id]['site_name']
    except KeyError:
        site_name = rbs_id
    return site_name


def get_ip(sites, rbs_id):
    """
    Get ip address from sites pool by rbs_id.

    Args:
        sites: dict
        rbs_id: string

    Returns:
        string
    """
    try:
        ip_address = sites[rbs_id]['ip_address']
    except KeyError:
        ip_address = None
    return ip_address


def parse_iub_link(utran_cell_tag):
    """
    Parse cells IubLink.

    Args:
        utran_cell_tag: xml tag object

    Returns:
        string
    """
    iub_link_ref = parse_attributes_value(utran_cell_tag, 'utranCellIubLink')
    return iub_link_ref.split('=')[-1]


def parse_wcdma_cells(xml_path, enm_sites, enm_ips, atoll_data):
    """
    Parse all necessary wcdma cell parameters.

    Args:
        xml_path: string
        enm_sites: dict
        enm_ips: dict
        atoll_data: dict

    Returns:
        list of dict
    """
    root = ElementTree.parse(xml_path).getroot()
    sites = parse_rbs_data(root, enm_sites, enm_ips)
    rbs_ids = parse_iublink_data(root)

    wcdma_cells = []
    for rnc_tag in root.iter(make_tag('MeContext', xn_ns)):
        rnc_name = rnc_tag.get(id_attr)
        if 'RNC' not in rnc_name:
            continue
        for rnc_id_tag in rnc_tag.iter(make_tag('rncId', un_ns)):
            rnc_id = rnc_id_tag.text

        for utran_cell_tag in rnc_tag.iter(make_tag('UtranCell', un_ns)):
            iub_link = parse_iub_link(utran_cell_tag)
            rbs_id = rbs_ids[iub_link]
            (
                mocn_cell_profile,
                administrative_state,
                qrxlevmin,
                qqualmin,
            ) = parse_data_utran_cell(utran_cell_tag)
            cell = {
                'operator': 'Kcell',
                'oss': 'OSS',
                'rnc_id': rnc_id,
                'rnc_name': rnc_name,
                'site_name': get_site_name(sites, rbs_id),
                'cell_name': utran_cell_tag.get(id_attr),
                'cId': parse_attributes_value(utran_cell_tag, 'cId'),
                'localCellId': parse_attributes_value(
                    utran_cell_tag,
                    'localCellId',
                ),
                'uarfcnDl': parse_attributes_value(utran_cell_tag, 'uarfcnDl'),
                'uarfcnUl': parse_attributes_value(utran_cell_tag, 'uarfcnUl'),
                'primaryScramblingCode': parse_attributes_value(
                    utran_cell_tag,
                    'primaryScramblingCode',
                ),
                'LocationArea': parse_attributes_value(utran_cell_tag, 'lac'),
                'RoutingArea': parse_attributes_value(utran_cell_tag, 'rac'),
                'ServiceArea': parse_attributes_value(utran_cell_tag, 'sac'),
                'Ura': parse_attributes_value(utran_cell_tag, 'uraList'),
                'primaryCpichPower': parse_attributes_value(
                    utran_cell_tag,
                    'primaryCpichPower',
                ),
                'maximumTransmissionPower': parse_attributes_value(
                    utran_cell_tag,
                    'maximumTransmissionPower',
                ),
                'IubLink': iub_link,
                'MocnCellProfile': mocn_cell_profile,
                'administrativeState': administrative_state,
                'ip_address': get_ip(sites, rbs_id),
                'vendor': 'Ericsson',
                'insert_date': date.today(),
                'qRxLevMin': qrxlevmin,
                'qQualMin': qqualmin,
            }
            wcdma_cells.append(
                add_physical_params(atoll_data, cell),
            )
    return wcdma_cells


def wcdma_main(atoll_data):
    """
    Prepare enm wcdma cell data for Network Live.

    Args:
        atoll_data (dict): a dict of cell physical params

    Returns:
        list: a list of dicts containing the parameters for each WCDMA cell
    """
    enm1_rbs_data = EnmCli.execute_cli_command('ENM1', 'wcdma_rbs_ids')
    enm2_rbs_data = EnmCli.execute_cli_command('ENM2', 'wcdma_rbs_ids')
    enm_sites = parse_node_parameter(enm1_rbs_data + enm2_rbs_data, 'MeContext')

    enm1_bbu_ips = EnmCli.execute_cli_command('ENM1', 'bbu_ips')
    enm2_bbu_ips = EnmCli.execute_cli_command('ENM2', 'bbu_ips')
    bbu_oam_ips = parse_bbu_ips(enm1_bbu_ips + enm2_bbu_ips, 'oam')

    enm1_dus_oam_ips = EnmCli.execute_cli_command('ENM1', 'dus_oam_ips')
    enm2_dus_oam_ips = EnmCli.execute_cli_command('ENM2', 'dus_oam_ips')
    dus_oam_ips = parse_node_parameter(
        enm1_dus_oam_ips + enm2_dus_oam_ips,
        'MeContext',
    )

    xml_path = 'logs/oss/oss_utrancells.xml'

    bcg_result = collect_oss_logs('WCDMA')
    if 'Export has succeeded' in bcg_result:
        xml_path = download_oss_logs('WCDMA')
        return parse_wcdma_cells(
            xml_path,
            enm_sites,
            {**bbu_oam_ips, **dus_oam_ips},
            atoll_data,
        )
