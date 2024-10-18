from datetime import date

from network_live.physical_params import add_physical_params
from network_live.zte.select_data import select_zte_data
from network_live.check_region import add_region, read_udrs


def parse_gsm_cells(zte_gsm_data, atoll_data, udrs):
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
            cell_with_phys_params = add_physical_params(atoll_data, cell)
            gsm_cells.append(
                add_region(cell_with_phys_params, udrs),
            )
        else:
            bcch_trx_cells.append(cell)

    for bcch_cell in bcch_trx_cells:
        one_trx_cells = []
        for gsm_cell in gsm_cells:
            if gsm_cell['cell_name'] == bcch_cell['cell_name']:
                if gsm_cell['bsc_name'] == bcch_cell['bsc_name']:
                    one_trx_cells.append(gsm_cell)

        if not one_trx_cells:
            cell_with_phys_params = add_physical_params(atoll_data, bcch_cell)
            gsm_cells.append(
                add_region(cell_with_phys_params, udrs),
            )

    return gsm_cells


def gsm_main(atoll_data):
    """
    Prepare  gsm cell data for Network Live.

    Args:
        atoll_data (dict): a dict of cell physical params

    Returns:
        list: a list of dicts containing the parameters for each GSM cell
    """
    zte_gsm_data = select_zte_data('gsm_cell')
    udrs = read_udrs()
    return parse_gsm_cells(zte_gsm_data, atoll_data, udrs)
