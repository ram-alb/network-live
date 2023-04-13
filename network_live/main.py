from network_live.atoll import select_atoll_data
from network_live.enm.enm_main import enm_main


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
    return enm_main(enm, technology, atoll_physical_params)
