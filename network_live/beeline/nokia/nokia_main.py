from network_live.beeline.nokia.gsm import gsm_main
from network_live.beeline.nokia.lte import lte_main
from network_live.beeline.nokia.wcdma import wcdma_main


def nokia_main(technology, atoll_data):
    """
    Return cells shared by Beeline on Nokia equipment.

    Args:
        technology (str): a RAN technology
        atoll_data (dict): a dict with cell physical params

    Returns:
        list: a list of dictionaries containing cell parameters
    """
    main_funcs = {
        'LTE': lte_main,
        'WCDMA': wcdma_main,
        'GSM': gsm_main,
    }

    return main_funcs[technology](atoll_data)
