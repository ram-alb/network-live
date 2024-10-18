from datetime import date

from network_live.enm.enm_cli import EnmCli
from network_live.enm.utils import (
    parse_bbu_ips,
    parse_fdn,
    parse_node_parameter,
)
from network_live.physical_params import add_physical_params
from network_live.check_region import read_udrs, add_region

attr_delimeter = ' : '


def parse_nr_sectors(enm_nr_sectors):
    """
    Parse NR sector information from an Ericsson Network Manager (ENM) dump.

    Args:
        enm_nr_sectors (list): a tuple of ElementGroups for NR sectors

    Returns:
        dict: a dict with sector names as keys and a dict of params as values
    """
    nr_sectors = {}
    for element in enm_nr_sectors:
        element_val = element.value()
        if 'FDN' in element_val:
            sector = parse_fdn(element_val, 'NRSectorCarrier')
            sector_params = {}
        elif attr_delimeter in element_val:
            attr_name, attr_value = element_val.split(attr_delimeter)
            sector_params[attr_name] = attr_value
            if attr_name == 'configuredMaxTxPower':
                nr_sectors[sector] = sector_params
    return nr_sectors


def get_extra_data(site_name, cell_name, nr_sectors, node_ids, node_ips):
    """
    Return a dictionary with extra data for a given cell.

    Args:
        site_name (str): a site name
        cell_name (str): a cell name
        nr_sectors (dict): a dict with NR sector data
        node_ids (dict): a dict with gNodeB IDs
        node_ips (dict): a dict with node IP addresses

    Returns:
        dict: a dict with extra data for the cell
    """
    return {
        'gNBId': node_ids[site_name],
        'arfcnDL': nr_sectors[cell_name]['arfcnDL'],
        'bSChannelBwDL': nr_sectors[cell_name]['bSChannelBwDL'],
        'configuredMaxTxPower': nr_sectors[cell_name]['configuredMaxTxPower'],
        'ip_address': node_ips[site_name],
        'vendor': 'Ericsson',
        'insert_date': date.today(),
    }


def get_nci(nci):
    """
    Return nCI for cell depending is nCI is numeric or not.

    Args:
        nci (str): a nCI for 5G cell

    Returns:
        union[str, None]
    """
    return nci if nci.isnumeric() else None


def parse_nr_cells(enm, enm_nr_cells, last_parameter, atoll_data, udrs, *args):
    """
    Parse NR cell information from an Ericsson Network Manager (ENM) dump.

    Args:
        enm (str): the name of the ENM
        enm_nr_cells (list): a tuple of ElementGroups for NR cells
        atoll_data (dict): a dict containing physical parameter information
        last_parameter (str): the name of the last parameter to parse for cells
        args (list): a list of extra data sourses

    Returns:
        list: a list of dictionaries containing NR cell information
    """
    nr_cells = []
    for element in enm_nr_cells:
        element_val = element.value()
        if 'FDN' in element_val:
            site_name = parse_fdn(element_val, 'MeContext')
            cell_name = parse_fdn(element_val, 'NRCellDU')
            extra_data = get_extra_data(site_name, cell_name, *args)
            cell = {
                'subnetwork': parse_fdn(element_val, 'SubNetwork'),
                'site_name': site_name,
                'cell_name': cell_name,
                'oss': enm,
                **extra_data,
            }
        elif attr_delimeter in element_val:
            attr_name, attr_value = element_val.split(attr_delimeter)
            cell[attr_name] = attr_value
            if attr_name == last_parameter:
                cell['nCI'] = get_nci(cell['nCI'])
                cell_with_phys_params = add_physical_params(atoll_data, cell)
                nr_cells.append(
                    add_region(cell_with_phys_params, udrs),
                )
    return nr_cells


def nr_main(enm, atoll_data):
    """
    Prepare enm nr cell data for Network Live.

    Args:
        enm (str): an ENM server number
        atoll_data (dict): a dict of cell physical params

    Returns:
        list: a list of dicts containing the parameters for each NR cell
    """
    enm_bbu_ips = EnmCli.execute_cli_command(enm, 'bbu_ips')
    bbu_oam_ips = parse_bbu_ips(enm_bbu_ips, 'router=oam')

    enm_nr_ids = EnmCli.execute_cli_command(enm, 'gnbid')
    gnbids = parse_node_parameter(enm_nr_ids, 'MeContext')

    enm_nr_sectors = EnmCli.execute_cli_command(enm, 'nr_sectors')
    nr_sectors = parse_nr_sectors(enm_nr_sectors)

    last_parameter = sorted(EnmCli.nr_cell_params)[-1]

    udrs = read_udrs()
    enm_nr_cells = EnmCli.execute_cli_command(enm, 'nr_cells')
    return parse_nr_cells(
        enm,
        enm_nr_cells,
        last_parameter,
        atoll_data,
        udrs,
        nr_sectors,
        gnbids,
        bbu_oam_ips,
    )
