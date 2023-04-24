from dotenv import load_dotenv
from network_live.main import update_nl

load_dotenv()


def main():
    print(update_nl())
