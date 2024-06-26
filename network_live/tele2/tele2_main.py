from network_live.tele2.gsm import gsm_main
from network_live.tele2.lte import lte_main
from network_live.tele2.nr import nr_main
from network_live.tele2.wcdma import wcdma_main


def tele2_main(technology, atoll_data):
    """
    Return a list of dicts with cell parameters of specified technology.

    Parameters:
        technology (str): the RAN technology to query
        atoll_data (dict): a dict with cell physical params

    Returns:
        list: a list of dictionaries containing cell parameters
    """
    main_funcs = {
        'LTE': lte_main,
        'WCDMA': wcdma_main,
        'GSM': gsm_main,
        'NR': nr_main,
    }

    return main_funcs[technology](atoll_data)
