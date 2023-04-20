import os

import paramiko


def run_oss_command(command):
    """
    Run the command on astoss.

    Args:
        command: string

    Returns:
        string
    """
    with paramiko.SSHClient() as client:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=os.getenv('ASTOSS_HOST'),
            username=os.getenv('ASTOSS_USER'),
            password=os.getenv('ASTOSS_PASSWORD'),
            port=os.getenv('ASTOSS_PORT'),
        )
        stdin, stdout, stderr = client.exec_command(command)
        oss_result = stdout.read() + stderr.read()
        return oss_result.decode()


def collect_oss_logs(technology):
    """
    Run oss bcgtool to generate wcdma cells xml file.

    Args:
        technology: string

    Returns:
        string
    """
    if technology == 'WCDMA':
        filter_path = '~/bcg_filters/WCDMA_custom_filter.xml'
        export_path = '~/bcg_filters/export/oss_utrancells.xml'
        bcgtool_path = '/opt/ericsson/nms_umts_wran_bcg/bin/bcgtool.sh'
        oss_command = '{bcgtool} -d {filter_path} -e {export_path}'.format(
            bcgtool=bcgtool_path,
            filter_path=filter_path,
            export_path=export_path,
        )
    elif technology == 'GSM':
        export_path = os.path.join(
            '/var/opt/ericsson/',
            'cnai/data/export/',
            'network_live_gsm_export.txt',
        )
        rm_old_export_command = f'rm {export_path}'
        run_oss_command(rm_old_export_command)

        cna_tool_path = '/opt/ericsson/bin/cna_export'
        cna_params = [
            'NW=all',
            'MSC=all',
            'MSC_REF=none',
            'BSC=all',
            'BSC_REF=none',
            'SITE=all',
            'SITE_REF=none',
            'CELL=all',
            'CELL_REF=network_live_gsm_filter.txt',
            'OUTPUT=network_live_gsm_export.txt',
        ]
        oss_command = '{cna_tool_path} {cna_params}'.format(
            cna_tool_path=cna_tool_path,
            cna_params=','.join(cna_params),
        )
    return run_oss_command(oss_command)
