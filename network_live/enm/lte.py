from datetime import date

from network_live.enm.utils import parse_fdn


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


def parse_lte_cells_params(enm_lte_cells, enodeb_ids, node_ips):
    """
    Parse the parameters for all LTE cells.

    Args:
        enm_lte_cells (tuple): a tuple of ElementGroups for LTE
        enodeb_ids (dict): a dictionary of eNodeB IDs keyed by site name
        node_ips (dict): a dictionary of IP addresses keyed by site name

    Returns:
        list: a list of dicts containing the parameters for each LTE cell
    """
    lte_cells = []
    for element in enm_lte_cells:
        element_val = element.value()
        if 'FDN' in element_val:
            site_name = parse_fdn(element_val, 'MeContext')
            cell = {
                'subnetwork': parse_fdn(element_val, 'SubNetwork'),
                'site_name': site_name,
                'cell_name': parse_fdn(element_val, 'EUtranCellFDD'),
                'vendor': 'Ericsson',
                'insert_date': date.today(),
            }
        elif ' : ' in element_val:
            attr_name, attr_value = element_val.split(' : ')
            if attr_name == 'tac':
                cell['tac'] = attr_value
                cell['enodeb_id'] = enodeb_ids[site_name]
                cell['eci'] = calculate_eci(cell['enodeb_id'], cell['cellId'])
                cell['ip_address'] = node_ips[site_name]
                lte_cells.append(cell)
            else:
                cell[attr_name] = attr_value
    return lte_cells
