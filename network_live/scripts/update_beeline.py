from dotenv import load_dotenv
from network_live.beeline.huawei.gsm import gsm_main
from network_live.main import update_beeline

load_dotenv()


def update_huawei_lte():
    """Update Network Live with Huawei LTE cells."""
    print(update_beeline('Huawei', 'LTE'))


def update_huawei_wcdma():
    """Update Network Live with Huawei WCDMA cells."""
    print(update_beeline('Huawei', 'WCDMA'))


def update_huawei_gsm():
    print(update_beeline('Huawei', 'GSM'))


def update_nokia_lte():
    """Update Network Live with Nokia LTE cells."""
    print(update_beeline('Nokia', 'LTE'))


def update_nokia_wcdma():
    """Update Network Live with Nokia WCDMA cells."""
    print(update_beeline('Nokia', 'WCDMA'))


def update_nokia_gsm():
    """Update Network Live with Nokia GSM cells."""
    print(update_beeline('Nokia', 'GSM'))
