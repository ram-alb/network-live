from network_live.enm.enm_main import enm_main
from network_live.oss.oss_main import oss_main
from network_live.tele2.tele2_main import tele2_main
from network_live.sql import select_atoll_data, update_network_live
from network_live.beeline.beeline_main import beeline_main


def update_enm(enm, technology):
    """
    Update Network Live database with enm cells for given technology.

    Args:
        enm (str): the ENM server number ('ENM1' or 'ENM2')
        technology (str): the RAN technology

    Returns:
        dict
    """
    atoll_physical_params = select_atoll_data(technology)
    cells = enm_main(enm, technology, atoll_physical_params)
    # return cells
    return update_network_live(cells, enm, technology)


def update_oss(technology):
    atoll_physical_params = select_atoll_data(technology)
    cells = oss_main(technology, atoll_physical_params)
    # return cells
    return update_network_live(cells, 'OSS', technology)


def update_tele2(technology):
    atoll_data = select_atoll_data(technology)
    cells = tele2_main(technology, atoll_data)
    # return cells
    return update_network_live(cells, 'Tele2', technology)


def update_beeline(vendor, technology):
    atoll_data = select_atoll_data(technology)
    cells = beeline_main(vendor, technology, atoll_data)
    # return cells
    return update_network_live(cells, f'Beeline {vendor}', technology)
