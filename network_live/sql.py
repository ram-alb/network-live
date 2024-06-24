import os

import cx_Oracle


def execute_sql(sql_type, sql_command, sql_params=None):
    """
    Execute the given SQL command against the Atoll database.

    Args:
        sql_type (str): the type of SQL command to execute.
        sql_command (str): the SQL command to execute.
        sql_params (list, optional): parameters to pass to the SQL command

    Returns:
        Union[None, list]: the results of the query in case of 'select' command
    """
    atoll_dsn = cx_Oracle.makedsn(
        os.getenv('ATOLL_HOST'),
        os.getenv('ATOLL_PORT'),
        service_name=os.getenv('SERVICE_NAME'),
    )
    with cx_Oracle.connect(
        user=os.getenv('ATOLL_LOGIN'),
        password=os.getenv('ATOLL_PASSWORD'),
        dsn=atoll_dsn,
    ) as connection:
        cursor = connection.cursor()
        if sql_type == 'delete':
            cursor.execute(sql_command)
            connection.commit()
        elif sql_type == 'insert':
            for cell in sql_params:
                if cell['rnc_name'] == 'AKTB_RNC_1':
                    print(cell)
                cursor.execute(sql_command, cell)
            connection.commit()
        elif sql_type == 'select':
            cursor.execute(sql_command)
            return cursor.fetchall()


def handle_atoll_data(selected_atoll_data):
    """
    Return a dictionary of physical parameters for each cell from atoll data.

    Args:
        selected_atoll_data (list): A list of tuples with physical parameters

    Returns:
        dict: a dict where key is the cell name and value is a dict with params
    """
    atoll_physical_params = {}
    for cell in selected_atoll_data:
        (
            cell_name,
            azimut,
            height,
            longitude,
            latitude,
        ) = cell
        atoll_physical_params[cell_name] = {
            'azimut': azimut,
            'height': height,
            'longitude': longitude,
            'latitude': latitude,
        }
    return atoll_physical_params


def select_atoll_data(technology):
    """
    Retrieve cell data with physical params from Atoll for a given technology.

    Args:
        technology (str): a string representing the RAN technology

    Returns:
        dict: a dict where key is the cell name and value is a dict with params
    """
    lte_select = """
        SELECT
            atoll_mrat.xgcellslte.cell_id,
            atoll_mrat.xgtransmitters.azimut,
            atoll_mrat.xgtransmitters.height,
            atoll_mrat.sites.longitude,
            atoll_mrat.sites.latitude
        FROM atoll_mrat.xgtransmitters
            INNER JOIN atoll_mrat.sites
                ON atoll_mrat.xgtransmitters.site_name = atoll_mrat.sites.name
            INNER JOIN atoll_mrat.xgcellslte
                ON atoll_mrat.xgtransmitters.tx_id = atoll_mrat.xgcellslte.tx_id
    """

    wcdma_select = """
        SELECT
            atoll_mrat.ucells.cell_id,
            atoll_mrat.utransmitters.azimut,
            atoll_mrat.utransmitters.height,
            atoll_mrat.sites.longitude,
            atoll_mrat.sites.latitude
        FROM atoll_mrat.utransmitters
            INNER JOIN atoll_mrat.sites
                ON atoll_mrat.utransmitters.site_name = atoll_mrat.sites.name
            INNER JOIN atoll_mrat.ucells
                ON atoll_mrat.utransmitters.tx_id = atoll_mrat.ucells.tx_id
    """

    gsm_select = """
        SELECT
            atoll_mrat.gtransmitters.tx_id,
            atoll_mrat.gtransmitters.azimut,
            atoll_mrat.gtransmitters.height,
            atoll_mrat.sites.longitude,
            atoll_mrat.sites.latitude
        FROM atoll_mrat.gtransmitters
            INNER JOIN atoll_mrat.sites
                ON atoll_mrat.gtransmitters.site_name = atoll_mrat.sites.name
    """

    nr_select = """
        SELECT
            atoll_mrat.xgcells5gnr.cell_id,
            atoll_mrat.xgtransmitters.azimut,
            atoll_mrat.xgtransmitters.height,
            atoll_mrat.sites.longitude,
            atoll_mrat.sites.latitude
        FROM
            atoll_mrat.xgtransmitters
        INNER JOIN atoll_mrat.xgcells5gnr
            ON atoll_mrat.xgcells5gnr.tx_id = atoll_mrat.xgtransmitters.tx_id
        INNER JOIN atoll_mrat.sites
            ON atoll_mrat.xgtransmitters.site_name = atoll_mrat.sites.name
    """

    sql_selects = {
        'LTE': lte_select,
        'WCDMA': wcdma_select,
        'GSM': gsm_select,
        'NR': nr_select,
    }

    return handle_atoll_data(execute_sql('select', sql_selects[technology]))


lte_insert_sql = """
    INSERT
        INTO ltecells2
    VALUES (
        :subnetwork,
        :enodeb_id,
        :site_name,
        :cell_name,
        :tac,
        :cellId,
        :eci,
        :earfcndl,
        :qRxLevMin,
        :administrativeState,
        :rachRootSequence,
        :physicalLayerCellId,
        :cellRange,
        :vendor,
        :ip_address,
        :oss,
        :azimut,
        :height,
        :longitude,
        :latitude,
        :insert_date,
        :primaryPlmnReserved
    )
"""

wcdma_insert_sql = """
    INSERT
        INTO wcdmacells2
    VALUES (
        :operator,
        :rnc_id,
        :rnc_name,
        :site_name,
        :cell_name,
        :localCellId,
        :cId,
        :uarfcnDl,
        :uarfcnUl,
        :primaryScramblingCode,
        :LocationArea,
        :RoutingArea,
        :ServiceArea,
        :Ura,
        :primaryCpichPower,
        :maximumTransmissionPower,
        :qRxLevMin,
        :qQualMin,
        :IubLink,
        :MocnCellProfile,
        :administrativeState,
        :ip_address,
        :vendor,
        :oss,
        :azimut,
        :height,
        :longitude,
        :latitude,
        :insert_date
    )
"""

gsm_insert_sql = """
    INSERT
        INTO gsmcells2
    VALUES (
        :operator,
        :bsc_id,
        :bsc_name,
        :site_name,
        :cell_name,
        :bcc,
        :ncc,
        :lac,
        :cell_id,
        :bcchNo,
        :hsn,
        :maio,
        :dchNo,
        :state,
        :vendor,
        :oss,
        :azimut,
        :height,
        :longitude,
        :latitude,
        :insert_date
    )
"""

nr_insert_sql = """
    INSERT
        INTO nrcells
    VALUES (
        :subnetwork,
        :gNBId,
        :site_name,
        :cell_name,
        :cellLocalId,
        :cellState,
        :nCI,
        :nRPCI,
        :nRTAC,
        :rachRootSequence,
        :qRxLevMin,
        :arfcnDL,
        :bSChannelBwDL,
        :configuredMaxTxPower,
        :ip_address,
        :vendor,
        :oss,
        :azimut,
        :height,
        :longitude,
        :latitude,
        :insert_date,
        :ssbFrequency
    )
"""


def update_network_live(cells, oss, technology):
    """
    Update Network Live with cells for given oss and technology.

    Args:
        cells (list): a list of dicts with cells parameters
        oss (str): an oss name
        technology (str): the RAN technology

    Returns:
        str: update result string
    """
    insert_sqls = {
        'LTE': lte_insert_sql,
        'WCDMA': wcdma_insert_sql,
        'GSM': gsm_insert_sql,
        'NR': nr_insert_sql,
    }
    network_live_tables = {
        'LTE': 'ltecells2',
        'WCDMA': 'wcdmacells2',
        'GSM': 'gsmcells2',
        'NR': 'nrcells',
    }

    delete_sql = "DELETE FROM {table} WHERE oss='{oss}'".format(
        table=network_live_tables[technology],
        oss=oss,
    )

    execute_sql('delete', delete_sql)
    try:
        execute_sql('insert', insert_sqls[technology], cells)
    except cx_Oracle.Error as err:
        err_obj, = err.args
        print(err_obj.code)
        print(err_obj.message)
        return f'{technology} {oss} Fail'
    return f'{technology} {oss} Success'
