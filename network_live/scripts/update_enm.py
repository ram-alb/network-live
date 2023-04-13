from dotenv import load_dotenv
from network_live.main import update_enm

load_dotenv()


def update_enm1_lte():
    """Update Network Live with ENM1 lte cells."""
    print(update_enm('ENM1', 'lte'))


def update_enm2_lte():
    """Update Network Live with ENM2 lte cells."""
    cells = update_enm('ENM2', 'lte')
    print(cells)
    print(len(cells[0].keys()))
