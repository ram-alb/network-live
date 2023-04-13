from network_live.sql import execute_sql


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
        'lte': lte_select,
        'wcdma': wcdma_select,
        'gsm': gsm_select,
        'nr': nr_select,
    }

    return handle_atoll_data(execute_sql('select', sql_selects[technology]))
