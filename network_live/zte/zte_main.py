from network_live.zte.wcdma import wcdma_main
from network_live.zte.gsm import gsm_main


def zte_main(technology, atoll_data):
    main_funcs = {
        'WCDMA': wcdma_main,
        'GSM': gsm_main,
    }

    return main_funcs[technology](atoll_data)
