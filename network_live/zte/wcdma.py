from datetime import date

from network_live.physical_params import add_physical_params
from network_live.zte.select_data import select_zte_data


def parse_wcdma_cells(zte_cell_data, zte_rnc_data, atoll_data):
    """
    Parse ZTE cell data.

    Args:
        zte_cell_data: list of tuples
        zte_rnc_data: list of tuples
        atoll_data: dict

    Returns:
        list of dicts
    """
    rnc_names = {rnc_id: rnc_name for rnc_name, rnc_id in zte_rnc_data}

    wcdma_cells = []

    for cell_params in zte_cell_data:
        (
            rnc_id,
            nodeb_name,
            cell_name,
            cell_id,
            local_cell_id,
            uarfcndl,
            uarfcnul,
            psc,
            lac,
            rac,
            sac,
            uralist,
            primary_cpich_power,
            max_tx_power,
            iublinkref,
            qrxlevmin,
            qqualmin,
        ) = cell_params

        cell = {
            'operator': 'Kcell',
            'oss': 'ZTE',
            'rnc_id': rnc_id,
            'rnc_name': rnc_names[rnc_id],
            'site_name': nodeb_name.split(' ')[0],
            'cell_name': cell_name,
            'cId': cell_id,
            'localCellId': local_cell_id,
            'uarfcnDl': uarfcndl,
            'uarfcnUl': uarfcnul,
            'primaryScramblingCode': psc,
            'LocationArea': lac,
            'RoutingArea': rac,
            'ServiceArea': sac,
            'Ura': uralist,
            'primaryCpichPower': primary_cpich_power,
            'maximumTransmissionPower': max_tx_power,
            'IubLink': iublinkref.split('=')[-1],
            'MocnCellProfile': None,
            'administrativeState': 'UNLOCKED',
            'ip_address': None,
            'vendor': 'ZTE',
            'insert_date': date.today(),
            'qRxLevMin': qrxlevmin,
            'qQualMin': qqualmin,
        }
        wcdma_cells.append(
            add_physical_params(atoll_data, cell),
        )
    return wcdma_cells


def wcdma_main(atoll_data):
    """
    Prepare ZTE wcdma cell data for Network Live.

    Args:
        atoll_data (dict): a dict of cell physical params

    Returns:
        list: a list of dicts containing the parameters for each WCDMA cell
    """
    zte_rnc_data = select_zte_data('rnc')
    zte_wcdma_cell_data = select_zte_data('wcdma_cell')
    return parse_wcdma_cells(zte_wcdma_cell_data, zte_rnc_data, atoll_data)
