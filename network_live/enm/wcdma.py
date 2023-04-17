from network_live.enm.utils import parse_node_parameter, parse_bbu_ips, parse_fdn
from datetime import date
from network_live.enm.enm_cli import EnmCli
from network_live.physical_params import add_physical_params


def swap_keys_vals(dict_obj):
    """
    Swap keys and values in dictionary.

    Args:
        dict_obj (dict): a dict which should be swapped

    Returns:
        dict: a swapped dict
    """
    return {value: key for key, value in dict_obj.items()}


def parse_wcdma_site_names(enm_rnc_iublink_ips, enm_dus_iub_ips, enm_bbu_ips):
    """
    Parse site names by iublink ips on rnc and sites objects.

    Args:
        enm_rnc_iublink_ips (tuple): a tuple of ElementGroups RNC IubLink Ips
        enm_dus_iub_ips (tuple): a tuple of ElementGroups DUS IubLink Ips
        enm_bbu_ips (dict): a dict with bbu names and ips

    Returns:
        dict: a dict where keys - iub ips, values - site names
    """
    rnc_iublink_ips = parse_node_parameter(enm_rnc_iublink_ips, 'IubLink')

    dus_iub_ips = parse_node_parameter(enm_dus_iub_ips, 'MeContext')
    bbu_iub_ips = parse_bbu_ips(enm_bbu_ips, 'iub')
    site_iublink_ips = {**swap_keys_vals(dus_iub_ips), **swap_keys_vals(bbu_iub_ips)}

    site_names = {}
    for iublink, iub_ip in rnc_iublink_ips.items():
        try:
            site_names[iublink] = site_iublink_ips[iub_ip]
        except KeyError:
            site_names[iublink] = iublink

    return site_names


def parse_parameter(parameter_string):
    """
    Parse parameter name and value.

    Args:
        parameter_string (str): a string to parse parameter

    Returns:
        tuple: a tuple with parameter name and value
    """
    attr_name, attr_value = parameter_string.split(' : ')
    if attr_name.endswith('Ref'):
        name_and_value = attr_value.split(',')[-1]
        try:
            parameter_name, parameter_value = name_and_value.split('=')
        except ValueError:
            parameter_name = attr_name[:-3]
            parameter_value = None
        if parameter_name == 'Ura':
            return (parameter_name, parameter_value[:-1])
        return (parameter_name, parameter_value)

    return (attr_name, attr_value)


def get_extra_data(iublink, rnc_name, site_names, rnc_ids, node_ips):
    """
    Return a dictionary with extra data for a cell.

    Args:
        iublink (str): an iublink for cell
        rnc_name (str): an rnc name where cell is configured
        site_names (dict): a dict where keys - iub ips, values - site names
        rnc_ids (dict): a dict where keys - rnc name, values - rnc id
        node_ips (dict): a dict with node names and ips

    Returns:
        dict: a dict with extra data for the cell
    """
    site_name = site_names[iublink]

    try:
        ip_address = node_ips[site_name]
    except KeyError:
        ip_address = None

    return {
        'site_name': site_name,
        'rnc_id': rnc_ids[rnc_name],
        'ip_address': ip_address,
        'operator': 'Kcell',
        'vendor': 'Ericsson',
        'insert_date': date.today(),
    }


def parse_wcdma_cells(enm, enm_wcdma_cells, last_parameter, atoll_data, *args):
    """
    Parse the parameters for all WCDMA cells.

    Args:
        enm (str): an ENM server number
        enm_wcdma_cells (tuple): a tuple of ElementGroups for wcdma cells
        last_parameter (str): the name of the last parameter to parse for cells
        atoll_data (dict): a dict of cell physical params
        args (list): a list of extra data sourses

    Returns:
        list: a list of dicts containing the parameters for each WCDMA cell
    """
    attr_delimeter = ' : '
    wcdma_cells = []
    for element in enm_wcdma_cells:
        element_val = element.value()
        if 'FDN' in element_val:
            cell = {
                'oss': enm,
                'rnc_name': parse_fdn(element_val, 'MeContext'),
                'cell_name': parse_fdn(element_val, 'UtranCell'),
            }
        elif attr_delimeter in element_val:
            parameter_name, parameter_value = parse_parameter(element_val)
            cell[parameter_name] = parameter_value
            if parameter_name.lower() in last_parameter.lower():
                extra_data = get_extra_data(cell['IubLink'], cell['rnc_name'], *args)
                wcdma_cells.append(
                    add_physical_params(atoll_data, {**cell, **extra_data}),
                )
    return wcdma_cells


def wcdma_main(enm, atoll_data):
    """
    Prepare WCDMA cell data to update Network Live db.

    Args:
        enm (str): an ENM server number
        atoll_data (dict): a dict of cell physical params

    Returns:
        dict: a dict with wcdma cell data
    """
    enm_rnc_iublink_ips = EnmCli.execute_cli_command(enm, 'rnc_iublink_ips')
    enm_dus_iub_ips = EnmCli.execute_cli_command(enm, 'dus_iub_ips')
    enm_bbu_ips = EnmCli.execute_cli_command(enm, 'bbu_ips')
    site_names = parse_wcdma_site_names(enm_rnc_iublink_ips, enm_dus_iub_ips, enm_bbu_ips)

    enm_dus_oam_ips = EnmCli.execute_cli_command(enm, 'dus_oam_ips')
    dus_oam_ips = parse_node_parameter(enm_dus_oam_ips, 'MeContext')
    bbu_oam_ips = parse_bbu_ips(enm_bbu_ips, 'oam')
    node_oam_ips = {**bbu_oam_ips, **dus_oam_ips}

    enm_rnc_ids = EnmCli.execute_cli_command(enm, 'rnc_ids')
    rnc_ids = parse_node_parameter(enm_rnc_ids, 'MeContext')

    last_parameter = sorted(EnmCli.wcdma_cell_params)[-1]
    enm_wcdma_cells = EnmCli.execute_cli_command(enm, 'wcdma_cells')
    wcdma_cells = parse_wcdma_cells(enm, enm_wcdma_cells, last_parameter, atoll_data, site_names, rnc_ids, node_oam_ips)
    return wcdma_cells
