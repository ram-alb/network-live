from dotenv import load_dotenv
from network_live.main import update_enm

load_dotenv()


def update_enm4_lte():
    """Update Network Live with ENM1 lte cells."""
    print(update_enm('ENM4', 'LTE'))


def update_enm2_lte():
    """Update Network Live with ENM2 lte cells."""
    print(update_enm('ENM2', 'LTE'))


def update_enm4_nr():
    """Update Network Live with ENM1 nr cells."""
    print(update_enm('ENM4', 'NR'))


def update_enm2_nr():
    """Update Network Live with ENM2 nr cells."""
    print(update_enm('ENM2', 'NR'))


def update_enm4_wcdma():
    """Update Network Live with ENM1 wcdma cells."""
    print(update_enm('ENM4', 'WCDMA'))


def update_enm2_wcdma():
    """Update Network Live with ENM2 wcdma cells."""
    print(update_enm('ENM2', 'WCDMA'))


def update_enm4_gsm():
    """Update Network Live with ENM1 gsm cells."""
    print(update_enm('ENM4', 'GSM'))


def update_enm2_gsm():
    """Update Network Live with ENM2 gsm cells."""
    print(update_enm('ENM2', 'GSM'))
