from network_live.tele2.gsm import gsm_main
from network_live.tele2.lte import lte_main
from network_live.tele2.wcdma import wcdma_main


def tele2_main(technology, atoll_data):
    main_funcs = {
        'LTE': lte_main,
        'WCDMA': wcdma_main,
        'GSM': gsm_main,
    }

    return main_funcs[technology](atoll_data)
