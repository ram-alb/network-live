from dotenv import load_dotenv
from network_live.enm.enm_main import enm_main

load_dotenv()


def main_enm1():
    print(enm_main('enm1', 'LTE'))


def main_enm2():
    print(enm_main('enm2', 'LTE'))
