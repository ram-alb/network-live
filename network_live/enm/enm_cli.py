import os

import enmscripting


class EnmCli(object):
    """Handle the execution of CLI commands on an Ericsson ENM server."""

    nr_cell_params = [
        'cellLocalId',
        'cellState',
        'nCI',
        'nRPCI',
        'nRTAC',
        'qRxLevMin',
        'rachRootSequence',
        'ssbFrequency',
    ]

    nr_sector_params = [
        'arfcnDL',
        'bSChannelBwDL',
        'configuredMaxTxPower',
    ]

    lte_cell_params = [
        'administrativeState',
        'cellId',
        'earfcndl',
        'physicalLayerCellId',
        'qRxLevMin',
        'rachRootSequence',
        'tac',
        'cellRange',
        'primaryPlmnReserved',
    ]

    wcdma_cell_params = [
        'cId',
        'localCellId',
        'uarfcnDl',
        'uarfcnUl',
        'primaryScramblingCode',
        'locationAreaRef',
        'routingAreaRef',
        'serviceAreaRef',
        'uraRef',
        'primaryCpichPower',
        'maximumTransmissionPower',
        'iubLinkRef',
        'mocnCellProfileRef',
        'administrativeState',
        'qRxLevMin',
        'qQualMin',
    ]

    gsm_cell_params = [
        'bcc',
        'ncc',
        'cgi',
        'bcchNo',
        'state',
    ]

    gsm_channel_params = [
        'channelGroupId==1',
        'hsn',
        'maio',
        'dchNo',
    ]

    cli_commands = {
        'nr_cells': 'cmedit get * NRCellDU.({params})'.format(
            params=','.join(nr_cell_params),
        ),
        'nr_sectors': 'cmedit get * NRSectorCarrier.({params})'.format(
            params=','.join(nr_sector_params),
        ),
        'gnbid': 'cmedit get * GNBDUFunction.(gNBId)',
        'lte_cells': 'cmedit get * EutranCellFdd.({params})'.format(
            params=','.join(lte_cell_params),
        ),
        'enodeb_id': 'cmedit get * ENodeBFunction.(enbid)',
        'wcdma_cells': 'cmedit get * UtranCell.({params})'.format(
            params=','.join(wcdma_cell_params),
        ),
        'rnc_ids': 'cmedit get * RncFunction.(rncId)',
        'rnc_iublink_ips': 'cmedit get *RNC* IubLink.(remoteCpIpAddress1)',
        'dus_iub_ips': 'cmedit get * IpAccessHostEt.(ipAddress)',
        'wcdma_rbs_ids': 'cmedit get * Iub.(rbsId)',
        'dus_oam_ips': 'cmedit get * Ip.(nodeIpAddress)',
        'bbu_ips': 'cmedit get * AddressIPv4.(address)',
        'gsm_bbu_sites': 'cmedit get * gsmsector.(bscNodeIdentity)',
        'gsm_tg12_sites': 'cmedit get * G12Tg.(rSite, connectedChannelGroup)',
        'gsm_tg31_sites': 'cmedit get * G31Tg.(rSite, connectedChannelGroup)',
        'gsm_cells': 'cmedit get * GeranCell.({params})'.format(
            params=','.join(gsm_cell_params),
        ),
        'channel_group': 'cmedit get * ChannelGroup.({params})'.format(
            params=','.join(gsm_channel_params),
        ),
        'bsc_ids': 'cmedit get * Bsc.(bscId)',
        'all_rnc': 'cmedit get *RNC*',
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
        if enm_number == 'ENM1':
            enm_server = os.getenv('ENM_SERVER_1')
        elif enm_number == 'ENM2':
            enm_server = os.getenv('ENM_SERVER_2')
        elif enm_number == 'ENM4':
            enm_server = os.getenv('ENM_SERVER_4')
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
