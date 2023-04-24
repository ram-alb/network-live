from dotenv import load_dotenv
from network_live.main import update_nl

load_dotenv()


def main():
    """Update Network Live with all cells."""
    print(update_nl())
