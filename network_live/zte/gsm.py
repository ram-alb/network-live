from network_live.zte.select_data import select_zte_data
from datetime import date
from network_live.physical_params import add_physical_params


def parse_gsm_cells(zte_gsm_data, atoll_data):
    """
    Parse ZTE GSM cell data.

    Args:
        zte_gsm_data: list of tuples
        atoll_data: dict

    Returns:
        list of dicts
    """
    gsm_cells = []
    bcch_trx_cells = []
    for gcell in set(zte_gsm_data):
        (
            bsc_id,
            bsc_name,
            site_name,
            cell_name,
            bcc,
            ncc,
            lac,
            cell_id,
            bcch,
            tch_freqs,
        ) = gcell
        cell = {
            'operator': 'Kcell',
            'oss': 'ZTE',
            'bsc_id': bsc_id,
            'bsc_name': bsc_name,
            'site_name': site_name,
            'cell_name': cell_name,
            'bcc': bcc,
            'ncc': ncc,
            'lac': lac,
            'cell_id': cell_id,
            'bcchNo': bcch,
            'hsn': None,
            'maio': None,
            'dchNo': tch_freqs,
            'state': 'Active',
            'vendor': 'ZTE',
            'insert_date': date.today(),
        }
        if tch_freqs:
            gsm_cells.append(
                add_physical_params(atoll_data, cell),
            )
        else:
            bcch_trx_cells.append(cell)

    for bcch_cell in bcch_trx_cells:
        one_trx_cells = list(filter(
            lambda cell: cell['cell_name'] == bcch_cell['cell_name'] and cell['bsc_name'] == bcch_cell['bsc_name'],
            gsm_cells,
        ))
        if not one_trx_cells:
            gsm_cells.append(
                add_physical_params(atoll_data, bcch_cell),
            )

    return gsm_cells


def gsm_main(atoll_data):
    zte_gsm_data = select_zte_data('gsm_cell')
    return parse_gsm_cells(zte_gsm_data, atoll_data)
