from network_live.beeline.huawei.huawei_main import huawei_main
from network_live.beeline.nokia.nokia_main import nokia_main
from network_live.beeline.zte.zte_main import beeline_zte_main

def beeline_main(vendor, technology, atoll_data):
    """
    Return a list of dicts with cell parameters of specified technology.

    Parameters:
        vendor (str): a vendor name used by Beeline (Huawei or Nokia)
        technology (str): the RAN technology to query
        atoll_data (dict): a dict with cell physical params

    Returns:
        list: a list of dictionaries containing cell parameters
    """
    main_funcs = {
        'Huawei': huawei_main,
        'Nokia': nokia_main,
        'ZTE': beeline_zte_main,
    }

    if vendor == 'ZTE':
        return main_funcs[vendor](technology)
    else:
        return main_funcs[vendor](technology, atoll_data)
