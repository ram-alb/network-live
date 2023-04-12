import os

import enmscripting


class EnmCli(object):
    """Handle the execution of CLI commands on an Ericsson ENM server."""

    eutrancell_params = [
        'administrativeState',
        'cellId',
        'earfcndl',
        'physicalLayerCellId',
        'qRxLevMin',
        'rachRootSequence',
        'tac',
        'cellRange',
    ]

    cli_commands = {
        'lte_cells': 'cmedit get * EutranCellFdd.({params})'.format(
            params=','.join(eutrancell_params),
        ),
        'enodeb_id': 'cmedit get * ENodeBFunction.(enbid)',
        'bbu_ip': 'cmedit get * AddressIPv4.(address)',
        'dus_ip': 'cmedit get * Ip.(nodeIpAddress)',
    }

    @classmethod
    def execute_cli_command(cls, enm_number, command):
        """
        Connect and execute the given CLI command on a given ENM server.

        Args:
            enm_number (str): the ENM server number to connect to
            command (str): the CLI command to execute.

        Returns:
            str: the response from the ENM after executing the CLI command
        """
        if enm_number == 'enm1':
            enm_server = os.getenv('ENM_SERVER_1')
        elif enm_number == 'enm2':
            enm_server = os.getenv('ENM_SERVER_2')

        session = enmscripting.open(enm_server).with_credentials(
            enmscripting.UsernameAndPassword(
                os.getenv('ENM_LOGIN'),
                os.getenv('ENM_PASSWORD'),
            ),
        )
        enm_cmd = session.command()
        response = enm_cmd.execute(cls.cli_commands[command])
        enmscripting.close(session)
        return response.get_output()
