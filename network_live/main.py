from anpusr_mail import send_email
from network_live.beeline.beeline_main import beeline_main
from network_live.enm.enm_main import enm_main
from network_live.oss.oss_main import oss_main
from network_live.sql import select_atoll_data, update_network_live
from network_live.tele2.tele2_main import tele2_main
from network_live.zte.zte_main import zte_main


def update_enm(enm, technology):
    """
    Update Network Live database with enm cells for given technology.

    Args:
        enm (str): the ENM server number ('ENM1' or 'ENM2')
        technology (str): the RAN technology

    Returns:
        str: update result
    """
    atoll_physical_params = select_atoll_data(technology)
    cells = enm_main(enm, technology, atoll_physical_params)
    return update_network_live(cells, enm, technology)


def update_oss(technology):
    """
    Update Network Live database with OSS cells for given technology.

    Args:
        technology (str): the RAN technology

    Returns:
        str: update result
    """
    atoll_physical_params = select_atoll_data(technology)
    cells = oss_main(technology, atoll_physical_params)
    return update_network_live(cells, 'OSS', technology)


def update_tele2(technology):
    """
    Update Network Live database with Tele2 cells for given technology.

    Args:
        technology (str): the RAN technology

    Returns:
        str: update result
    """
    atoll_data = select_atoll_data(technology)
    cells = tele2_main(technology, atoll_data)
    return update_network_live(cells, 'Tele2', technology)


def update_beeline(vendor, technology):
    """
    Update Network Live database with Beeline cells for given technology.

    Args:
        vendor (str): a vendor name (Huawei or Nokia)
        technology (str): the RAN technology

    Returns:
        str: update result
    """
    atoll_data = select_atoll_data(technology)
    cells = beeline_main(vendor, technology, atoll_data)
    return update_network_live(cells, f'Beeline {vendor}', technology)


def update_zte(technology):
    """
    Update Network Live database with ZTE cells for given technology.

    Args:
        technology (str): the RAN technology

    Returns:
        str: update result
    """
    atoll_data = select_atoll_data(technology)
    cells = zte_main(technology, atoll_data)
    return update_network_live(cells, 'ZTE', technology)


def update_nl():
    """Update Network Live database with all cells for given technology."""
    technologies = ['NR', 'LTE', 'WCDMA', 'GSM']
    atoll_data = {tech: select_atoll_data(tech) for tech in technologies}
    results = []

    """
    for enm in ('ENM2', 'ENM4'):
        for enm_tech in technologies:
            try:
                enm_cells = enm_main(enm, enm_tech, atoll_data[enm_tech])
                results.append(update_network_live(enm_cells, enm, enm_tech))
            except:
                results.append(f'{enm_tech} {enm} fail')
            print(results[-1])
    """

    """
    try:
        oss_cells = oss_main('GSM', atoll_data['GSM'])
        results.append(update_network_live(oss_cells, 'OSS', 'GSM'))
    except:
        results.append(f'{oss_zte_tech} OSS fail')
    print(results[-1])
    """

    """
    for oss_zte_tech in technologies[2:]:
        try:
            zte_cells = zte_main(oss_zte_tech, atoll_data[oss_zte_tech])
            results.append(update_network_live(zte_cells, 'ZTE', oss_zte_tech))
        except:
            results.append(f'{oss_zte_tech} ZTE fail')
        print(results[-1])
    """

    for tele2_tech in technologies:
        try:
            tele2_cells = tele2_main(tele2_tech, atoll_data[tele2_tech])
            results.append(update_network_live(tele2_cells, 'Tele2', tele2_tech))
        except:
            results.append(f'{tele2_tech} Tele2 fail')
        print(results[-1])

    for nokia_tech in technologies[1:]:
        try:
            bee_nokia_cells = beeline_main('Nokia', nokia_tech, atoll_data[nokia_tech])
            results.append(update_network_live(bee_nokia_cells, 'Beeline Nokia', nokia_tech))
        except:
            results.append(f'{nokia_tech} Beeline Nokia fail')
        print(results[-1])

    for bee_hua_tech in technologies[2:]:
        try:
            bee_hua_cells = beeline_main('Huawei', bee_hua_tech, atoll_data[bee_hua_tech])
            results.append(update_network_live(bee_hua_cells, 'Beeline Huawei', bee_hua_tech))
        except:
            results.append(f'{bee_hua_tech} Beeline Huawei fail')
        print(results[-1])

    # to = ['ramil.albakov@kcell.kz']
    # message = '\n'.join(sorted(results))
    # send_email(to, 'Network Live update report', message)