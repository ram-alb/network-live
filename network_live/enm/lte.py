from datetime import date

from network_live.enm.enm_cli import EnmCli
from network_live.enm.utils import (
    parse_bbu_ips,
    parse_fdn,
    parse_node_parameter,
)
from network_live.physical_params import add_physical_params


def get_extra_data(site_name, node_ids, node_ips):
    """
    Return a dictionary with extra data for a given cell.

    Args:
        site_name (str): a site name
        node_ids (dict): a dict with gNodeB IDs
        node_ips (dict): a dict with node IP addresses

    Returns:
        dict: a dict with extra data for the cell
    """
    return {
        'enodeb_id': node_ids[site_name],
        'ip_address': node_ips[site_name],
        'vendor': 'Ericsson',
        'insert_date': date.today(),
    }


def calculate_eci(enodeb_id, cell_id):
    """
    Calculate the E-UTRAN Cell Identifier (ECI) for an LTE cell.

    Args:
        enodeb_id (str): the eNodeB ID for the cell
        cell_id (str): the Cell ID for the cell

    Returns:
        int: the ECI for the cell
    """
    eci_factor = 256
    int_enodeb_id = int(enodeb_id)
    int_cell_id = int(cell_id)
    return int_enodeb_id * eci_factor + int_cell_id


def parse_lte_cells(enm, enm_lte_cells, last_parameter, atoll_data, *args):
    """
    Parse the parameters for all LTE cells.

    Args:
        enm (str): an ENM server number
        enm_lte_cells (tuple): a tuple of ElementGroups for LTE cells
        last_parameter (str): the name of the last parameter to parse for cells
        atoll_data (dict): a dict of cell physical params
        args (list): a list of extra data sourses

    Returns:
        list: a list of dicts containing the parameters for each LTE cell
    """
    lte_cells = []
    for element in enm_lte_cells:
        element_val = element.value()
        if 'FDN' in element_val:
            site_name = parse_fdn(element_val, 'MeContext')
            extra_data = get_extra_data(site_name, *args)
            cell = {
                'subnetwork': parse_fdn(element_val, 'SubNetwork'),
                'site_name': site_name,
                'cell_name': parse_fdn(element_val, 'EUtranCellFDD'),
                'oss': enm,
                **extra_data,
            }
        elif ' : ' in element_val:
            attr_name, attr_value = element_val.split(' : ')
            cell[attr_name] = attr_value
            if attr_name == last_parameter:
                cell['eci'] = calculate_eci(cell['enodeb_id'], cell['cellId'])
                lte_cells.append(add_physical_params(atoll_data, cell))
    return lte_cells


def lte_main(enm, atoll_data):
    """
    Prepare enm lte cell data for Network Live.

    Args:
        enm (str): an ENM server number
        atoll_data (dict): a dict of cell physical params

    Returns:
        list: a list of dicts containing the parameters for each LTE cell
    """
    enm_bbu_ips = EnmCli.execute_cli_command(enm, 'bbu_ips')
    bbu_oam_ips = parse_bbu_ips(enm_bbu_ips, 'router=oam')

    enm_dus_oam_ips = EnmCli.execute_cli_command(enm, 'dus_oam_ips')
    dus_oam_ips = parse_node_parameter(enm_dus_oam_ips, 'MeContext')

    enm_enbids = EnmCli.execute_cli_command(enm, 'enodeb_id')
    enbids = parse_node_parameter(enm_enbids, 'MeContext')

    node_ips = {**bbu_oam_ips, **dus_oam_ips}
    last_parameter = sorted(EnmCli.lte_cell_params)[-1]

    enm_lte_cells = EnmCli.execute_cli_command(enm, 'lte_cells')
    return parse_lte_cells(
        enm,
        enm_lte_cells,
        last_parameter,
        atoll_data,
        enbids,
        node_ips,
    )
