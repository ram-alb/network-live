def add_physical_params(atoll_data, cell_obj):
    """
    Add physical params to cell object.

    Args:
        atoll_data (dict): a dict of physical params dicts keyed by cell name
        cell_obj (dict): a dict of cell parameters

    Returns:
        dict: cell_obj with physical params
    """
    try:
        physical_params = atoll_data[cell_obj['cell_name']]
    except KeyError:
        physical_params = {
            'azimut': None,
            'height': None,
            'longitude': None,
            'latitude': None,
        }
    return {**cell_obj, **physical_params}
