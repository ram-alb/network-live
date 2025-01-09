def add_physical_params(atoll_data, technology, cell_obj):
    """
    Add physical params to cell object.

    Args:
        atoll_data (dict): a dict of physical params dicts keyed by cell name
        cell_obj (dict): a dict of cell parameters

    Returns:
        dict: cell_obj with physical params
    """
    physical_params = {}
    try:
        atoll_cell_data = atoll_data[technology][cell_obj['cell_name']]
        physical_params = {**atoll_cell_data}
    except KeyError:
        physical_params = {
            'azimut': None,
            'height': None,
            'longitude': None,
            'latitude': None,
        }

    if physical_params['longitude'] is None or physical_params['latitude'] is None:
        try:
            atoll_site_data = atoll_data['sites'][cell_obj['site_name']]
            physical_params['longitude'] = atoll_site_data['longitude']
            physical_params['latitude'] = atoll_site_data['latitude']
        except KeyError:
            physical_params['longitude'] = None
            physical_params['latitude'] = None

    return {**cell_obj, **physical_params}
