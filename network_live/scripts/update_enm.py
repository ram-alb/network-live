from dotenv import load_dotenv
from network_live.main import update_enm

load_dotenv()


def update_enm1_lte():
    """Update Network Live with ENM1 lte cells."""
    print(update_enm('ENM1', 'LTE'))


def update_enm2_lte():
    """Update Network Live with ENM2 lte cells."""
    print(update_enm('ENM2', 'LTE'))


def update_enm1_nr():
    """Update Network Live with ENM1 nr cells."""
    print(update_enm('ENM1', 'NR'))


def update_enm2_nr():
    """Update Network Live with ENM2 nr cells."""
    print(update_enm('ENM2', 'NR'))
