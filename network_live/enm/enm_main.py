from network_live.enm.enm_cli import EnmCli
from network_live.enm.lte import parse_lte_cells
from network_live.enm.nr5g import parse_nr_cells, parse_nr_sectors
from network_live.enm.utils import parse_bbu_ips, parse_node_parameter
from network_live.enm.wcdma import wcdma_main


def enm_main(enm, technology, atoll_data):
    """
    Return a list of dicts with cell parameters of specified technology.

    Parameters:
        enm (str): the ENM server number to query ('ENM1' or 'ENM2')
        technology (str): the RAN technology to query
        atoll_data (dict): a dict with cell physical params

    Returns:
        list: a list of dictionaries containing cell parameters
    """
    if technology in {'NR', 'LTE', 'WCDMA'}:
        enm_bbu_ips = EnmCli.execute_cli_command(enm, 'bbu_ips')
        bbu_oam_ips = parse_bbu_ips(enm_bbu_ips, 'router=oam')

        enm_dus_oam_ips = EnmCli.execute_cli_command(enm, 'dus_oam_ips')
        dus_oam_ips = parse_node_parameter(enm_dus_oam_ips, 'MeContext')

    if technology == 'NR':
        enm_nr_ids = EnmCli.execute_cli_command(enm, 'gnbid')
        gnbids = parse_node_parameter(enm_nr_ids, 'MeContext')

        enm_nr_sectors = EnmCli.execute_cli_command(enm, 'nr_sectors')
        nr_sectors = parse_nr_sectors(enm_nr_sectors)

        last_parameter = sorted(EnmCli.nr_cell_params)[-1]

        enm_nr_cells = EnmCli.execute_cli_command(enm, 'nr_cells')
        cells = parse_nr_cells(
            enm,
            enm_nr_cells,
            last_parameter,
            atoll_data,
            nr_sectors,
            gnbids,
            bbu_oam_ips,
        )
    elif technology == 'LTE':
        enm_enbids = EnmCli.execute_cli_command(enm, 'enodeb_id')
        enbids = parse_node_parameter(enm_enbids, 'MeContext')

        node_ips = {**bbu_oam_ips, **dus_oam_ips}
        last_parameter = sorted(EnmCli.lte_cell_params)[-1]

        enm_lte_cells = EnmCli.execute_cli_command(enm, 'lte_cells')
        cells = parse_lte_cells(
            enm,
            enm_lte_cells,
            last_parameter,
            atoll_data,
            enbids,
            node_ips,
        )
    elif technology == 'WCDMA':
        cells = wcdma_main(enm, atoll_data)
    return cells
