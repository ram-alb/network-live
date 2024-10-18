import re
from copy import deepcopy
from datetime import date

from deepmerge import always_merger
from network_live.enm.enm_cli import EnmCli
from network_live.enm.utils import parse_fdn
from network_live.physical_params import add_physical_params
from network_live.check_region import add_region, read_udrs

attr_delimeter = ' : '
fdn_label = 'FDN'
me_context = 'MeContext'


def parse_bbu_sites(enm_gsm_sites):
    """
    Parse BBU sites from the given Enm ElementGroup object.

    Args:
        enm_gsm_sites (tuple): a tuple of ElementGroups for bbu sites

    Returns:
        dict: a dict of bbu sites with the respective cell names and site names
    """
    sites = {}

    for element in enm_gsm_sites:
        element_val = element.value()
        if fdn_label in element_val:
            site_name = parse_fdn(element_val, me_context)
            cell_name = parse_fdn(element_val, 'GsmSector')
        elif 'bscNodeIdentity' in element_val:
            bsc_pattern = r'[a-z,A-Z]*_B\d{1,2}'
            try:
                bsc_name = re.search(bsc_pattern, element_val).group()
            except AttributeError:
                continue
            sites.setdefault(bsc_name, {})[cell_name] = site_name
    return sites


def parse_tg_sites(enm_tg_sites):
    """
    Parse sites configured on TG from the given Enm ElementGroup object.

    Args:
        enm_tg_sites (tuple): a tuple of ElementGroups for tg sites

    Returns:
        dict: a dict of tg sites with the respective cell names and site names
    """
    cell_pattern = 'GeranCell=[^,]*'
    sites = {}
    for element in enm_tg_sites:
        element_val = element.value()
        if fdn_label in element_val:
            bsc_name = parse_fdn(element_val, me_context)
        elif 'connectedChannelGroup' in element_val:
            connected_cells = re.findall(cell_pattern, element_val)
            gsm_cells = [
                cell.split('=')[-1] for cell in set(connected_cells)
            ]
        elif 'rSite' in element_val:
            site_name = element_val.split(attr_delimeter)[-1]
            for cell in gsm_cells:
                sites.setdefault(bsc_name, {})[cell] = site_name
    return sites


def get_site_name(bsc_name, cell_name, sites):
    """
    Get site name by bsc name and cell name.

    Args:
        bsc_name (str): a bsc name
        cell_name (str): a cell name
        sites (dict): a dict of sites

    Returns:
        Union[str, None]: a site name
    """
    try:
        site_name = sites[bsc_name][cell_name]
    except KeyError:
        site_name = None
    return site_name


def parse_channel_group(enm_channel_group):
    """
    Parse channel group configuration data from an Enm ElementGroup object.

    Args:
        enm_channel_group (tuple): a tuple of ElementGroup objects

    Returns:
        dict: a nested dict containing channel group configuration data
    """
    channel_data = {}
    for element in enm_channel_group:
        element_val = element.value()
        if fdn_label in element_val:
            bsc_name = parse_fdn(element_val, me_context)
            cell_name = parse_fdn(element_val, 'ChannelGroupCell')
            channel_data.setdefault(bsc_name, {})[cell_name] = {}
        elif attr_delimeter in element_val:
            parameter_name, parameter_value = element_val.split(attr_delimeter)
            if parameter_name in {'dchNo', 'maio'}:
                parameter_value = parameter_value[1:-1]
            elif parameter_name == 'channelGroupId':
                continue
            channel_data[bsc_name][cell_name][parameter_name] = parameter_value
    return channel_data


def get_extra_data(cell_name, bsc_name, sites, channel_data):
    """
    Return a dictionary with extra data for a given cell.

    Args:
        cell_name (str): a cell name
        bsc_name (str): a bsc name
        sites (dict): a dict with site names
        channel_data (dict): a dict with channel group params

    Returns:
        dict: a dict with extra data for the cell
    """
    extra_data = {
        'operator': 'Kcell',
        'bsc_id': '1',
        'site_name': get_site_name(bsc_name, cell_name, sites),
        'vendor': 'Ericsson',
        'insert_date': date.today(),
    }
    try:
        extra_data.update(channel_data[bsc_name][cell_name])
    except KeyError:
        extra_data['dchNo'] = None
        extra_data['hsn'] = None
        extra_data['maio'] = None
    return extra_data


def add_parameter(cell, parameter_str):
    """
    Add cell level parameter for cell object.

    Args:
        cell (dict): a dict with cell data
        parameter_str (str): a str containing parameter name and value
    """
    parameter_name, parameter_value = parameter_str.split(attr_delimeter)
    if parameter_name == 'cgi':
        if parameter_value == 'null':
            cell['lac'] = None
            cell['cell_id'] = None
        else:
            cell['lac'] = parameter_value.split('-')[-2]
            cell['cell_id'] = parameter_value.split('-')[-1]
    else:
        if parameter_value == 'null':
            cell[parameter_name] = None
        else:
            cell[parameter_name] = parameter_value


def parse_gsm_cells(enm, enm_gsm_cells, last_parameter, atoll_data, udrs, *args):
    """
    Parse the parameters for all GSM cells.

    Args:
        enm (str): an ENM server number
        enm_gsm_cells (tuple): a tuple of ElementGroups for GSM cells
        last_parameter (str): the name of the last parameter to parse for cells
        atoll_data (dict): a dict of cell physical params
        args (list): a list of extra data sourses

    Returns:
        list: a list of dicts containing the parameters for each GSM cell
    """
    gsm_cells = []
    for element in enm_gsm_cells:
        element_val = element.value()
        if fdn_label in element_val:
            bsc_name = parse_fdn(element_val, me_context)
            cell_name = parse_fdn(element_val, 'GeranCell')
            cell = {
                'bsc_name': bsc_name,
                'cell_name': cell_name,
                'oss': enm,
            }
        elif attr_delimeter in element_val:
            add_parameter(cell, element_val)
            extra_data = get_extra_data(cell_name, bsc_name, *args)
            cell.update(extra_data)
            if last_parameter in cell.keys():
                cell_with_phys_params = add_physical_params(atoll_data, cell)
                gsm_cells.append(add_region(cell_with_phys_params, udrs))
    return gsm_cells


def gsm_main(enm, atoll_data):
    """
    Prepare enm gsm cell data for Network Live.

    Args:
        enm (str): an ENM server number
        atoll_data (dict): a dict of cell physical params

    Returns:
        list: a list of dicts containing the parameters for each GSM cell
    """
    enm_gsm_bbu_sites = EnmCli.execute_cli_command(enm, 'gsm_bbu_sites')
    bbu_sites = parse_bbu_sites(enm_gsm_bbu_sites)

    enm_tg12_sites = EnmCli.execute_cli_command(enm, 'gsm_tg12_sites')
    tg12_sites = parse_tg_sites(enm_tg12_sites)

    enm_tg31_sites = EnmCli.execute_cli_command(enm, 'gsm_tg31_sites')
    tg31_sites = parse_tg_sites(enm_tg31_sites)

    sites = deepcopy(tg31_sites)
    always_merger.merge(sites, tg12_sites)
    always_merger.merge(sites, bbu_sites)

    enm_channel_data = EnmCli.execute_cli_command(enm, 'channel_group')
    channel_data = parse_channel_group(enm_channel_data)

    udrs = read_udrs()
    enm_gsm_cells = EnmCli.execute_cli_command(enm, 'gsm_cells')
    return parse_gsm_cells(
        enm,
        enm_gsm_cells,
        sorted(EnmCli.gsm_cell_params)[-1],
        atoll_data,
        udrs,
        sites,
        channel_data,
    )
