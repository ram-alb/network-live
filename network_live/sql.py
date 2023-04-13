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
            cursor.executemany(sql_command, sql_params)
            connection.commit()
        elif sql_type == 'select':
            cursor.execute(sql_command)
            return cursor.fetchall()


lte_insert_sql = """
    INSERT
        INTO ltecells3
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
        :insert_date
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
        :IubLink,
        :MocnCellProfile,
        :administrativeState,
        :ip_address,
        :vendor,
        :oss,
        :insert_date,
        :azimut,
        :height,
        :longitude,
        :latitude
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
        :tch_freqs,
        :state,
        :vendor,
        :insert_date,
        :oss,
        :azimut,
        :height,
        :longitude,
        :latitude
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
        :insert_date,
        :oss,
        :azimut,
        :height,
        :longitude,
        :latitude
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
        'LTE': 'ltecells3',
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
