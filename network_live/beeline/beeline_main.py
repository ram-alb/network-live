from network_live.beeline.huawei.huawei_main import huawei_main
from network_live.beeline.nokia.nokia_main import nokia_main


def beeline_main(vendor, technology, atoll_data):
    main_funcs = {
        'Huawei': huawei_main,
        'Nokia': nokia_main,
    }

    return main_funcs[vendor](technology, atoll_data)
