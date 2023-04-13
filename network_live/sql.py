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
