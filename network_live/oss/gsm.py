from datetime import date
from network_live.physical_params import add_physical_params
from network_live.oss.oss_ssh import collect_oss_logs
from network_live.ftp import download_oss_logs


def parse_hsn(gsm_params, line):
    """
    Parse hsn from line of log content.

    Args:
        gsm_params: list of strings
        line: string

    Returns:
        string
    """
    channel_group_index = gsm_params.index('ch_group_1')
    hsn = line.split(' ')[channel_group_index + 1]
    return None if hsn == 'NULL' else hsn


def parse_hopping_params(param_type, gsm_params, line):
    """
    Parse maio from line of log content.

    Args:
        param_type: string
        gsm_params: list of strings
        line: string

    Returns:
        string
    """
    index_delta = 8
    maio_start_delta = 2
    tch_start_delta = 10

    channel_group_index = gsm_params.index('ch_group_1')
    if param_type == 'maio':
        start_index = channel_group_index + maio_start_delta
        last_index = channel_group_index + maio_start_delta + index_delta
    elif param_type == 'tch':
        start_index = channel_group_index + tch_start_delta
        last_index = channel_group_index + tch_start_delta + index_delta
    hopp_param_list = [
        hopp for hopp in line.split(' ')[start_index:last_index] if hopp != 'NULL'
    ]
    return ', '.join(hopp_param_list)


def get_parameter_value(parameter_name, params_list, line):
    """
    Get parameter value by parameter name from line of log content.

    Args:
        parameter_name: string
        params_list: list
        line: string

    Returns:
        string
    """
    line_params = line.split(' ')
    parameter_value = line_params[params_list.index(parameter_name)]
    return None if parameter_value == 'NULL' else parameter_value


def parse_gsm_cells(log_path, atoll_data):
    """
    Parse GSM cell data from OSS txt log file.

    Args:
        log_path: string
        atoll_data: dict

    Returns:
        list of dicts
    """
    with open(log_path) as log:
        log_content = log.readlines()

    gsm_params = log_content[0].split(' ')
    gsm_cells = []
    for line in log_content[2:]:
        cell_name = get_parameter_value('CELL', gsm_params, line)
        if cell_name is None:
            continue
        cell = {
            'operator': 'Kcell',
            'oss': 'OSS',
            'bsc_id': None,
            'bsc_name': get_parameter_value('BSC', gsm_params, line),
            'site_name': get_parameter_value('SITE', gsm_params, line),
            'cell_name': cell_name,
            'bcc': get_parameter_value('bcc', gsm_params, line),
            'ncc': get_parameter_value('ncc', gsm_params, line),
            'lac': get_parameter_value('lac', gsm_params, line),
            'cell_id': get_parameter_value('ci', gsm_params, line),
            'bcchNo': get_parameter_value('bcchno', gsm_params, line),
            'hsn': parse_hsn(gsm_params, line),
            'maio': parse_hopping_params('maio', gsm_params, line),
            'dchNo': parse_hopping_params('tch', gsm_params, line),
            'state': get_parameter_value('cell_state', gsm_params, line),
            'vendor': 'Ericsson',
            'insert_date': date.today(),
        }
        gsm_cells.append(
            add_physical_params(atoll_data, cell),
        )
    return gsm_cells


def gsm_main(atoll_data):
    # cna_result = collect_oss_logs('GSM')
    log_path = 'logs/oss/network_live_gsm_export.txt'
    # if '100%' in cna_result:
        # log_path = download_oss_logs('GSM')

    return parse_gsm_cells(log_path, atoll_data)
