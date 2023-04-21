from network_live.beeline.huawei.lte import lte_main
from network_live.beeline.huawei.wcdma import wcdma_main


def huawei_main(technology, atoll_data):
    main_funcs = {
        'LTE': lte_main,
        'WCDMA': wcdma_main,
    }
    return main_funcs[technology](atoll_data)
