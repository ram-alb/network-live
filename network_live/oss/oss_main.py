from network_live.oss.gsm import gsm_main
from network_live.oss.wcdma import wcdma_main


def oss_main(technology, atoll_data):
    """
    Return a list of dicts with cell parameters of specified technology.

    Parameters:
        technology (str): the RAN technology to query
        atoll_data (dict): a dict with cell physical params

    Returns:
        list: a list of dictionaries containing cell parameters
    """
    main_funcs = {
        'WCDMA': wcdma_main,
        'GSM': gsm_main,
    }
    return main_funcs[technology](atoll_data)
