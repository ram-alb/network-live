from network_live.enm.gsm import gsm_main
from network_live.enm.lte import lte_main
from network_live.enm.nr5g import nr_main
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
    main_funcs = {
        'NR': nr_main,
        'LTE': lte_main,
        'WCDMA': wcdma_main,
        'GSM': gsm_main,
    }
    return main_funcs[technology](enm, atoll_data)
