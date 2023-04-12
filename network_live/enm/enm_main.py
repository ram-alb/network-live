from network_live.enm.enm_cli import EnmCli
from network_live.enm.lte import parse_lte_cells_params
from network_live.enm.utils import parse_bbu_ips, parse_node_parameter


def enm_main(enm, technology):
    """
    Return a list of dicts with cell parameters of specified technology.

    Parameters:
        enm (str): the ENM server number to query ('enm1' or 'enm2')
        technology (str): the RAN technology to query

    Returns:
        list: a list of dictionaries containing cell parameters
    """
    if technology == 'LTE':

        enm_enbids = EnmCli.execute_cli_command(enm, 'enodeb_id')
        enbids = parse_node_parameter(enm_enbids, 'MeContext')

        enm_bbu_ips = EnmCli.execute_cli_command(enm, 'bbu_ip')
        bbu_ips = parse_bbu_ips(enm_bbu_ips)

        enm_dus_ips = EnmCli.execute_cli_command(enm, 'dus_ip')
        dus_ips = parse_node_parameter(enm_dus_ips, 'MeContext')

        enm_lte_cells = EnmCli.execute_cli_command(enm, 'lte_cells')
        lte_cells = parse_lte_cells_params(
            enm_lte_cells,
            enbids,
            {**bbu_ips, **dus_ips},
        )
        return lte_cells