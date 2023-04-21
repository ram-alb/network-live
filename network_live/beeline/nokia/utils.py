import os


def make_tag(tag_name):
    """
    Make tag with namespace.

    Args:
        tag_name: string

    Returns:
        string
    """
    namespace = '{raml20.xsd}'
    return '{namespace}{tag}'.format(namespace=namespace, tag=tag_name)


def parse_sites(root, technology):
    """
    Parse site names from root tag object of Nokia xml file.

    Args:
        root: xml root object
        technology: string

    Returns:
        dict
    """
    sites = {}
    if technology == 'WCDMA':
        site_class = 'WBTS'
    elif technology == 'GSM':
        site_class = 'BCF'

    for site_tag in root.iter(make_tag('managedObject')):
        if site_tag.get('class') != site_class:
            continue
        site_id = site_tag.get('distName').split('/')[-1]
        for site_parameter_tag in site_tag.iter(make_tag('p')):
            if site_parameter_tag.get('name') == 'name':
                site_name = site_parameter_tag.text
                sites[site_id] = site_name
                break
    return sites


def parse_nodes(cell_tag):
    """
    Parse site id, controller name, controller id from cell tag.

    Args:
        cell_tag: xml tag object

    Returns:
        tuple
    """
    nodes = cell_tag.get('distName').split('/')
    site_id = nodes[-2]
    controller_name = nodes[-3]
    controller_id = controller_name.split('-')[-1]
    return (site_id, controller_name, controller_id)


def parse_cell_parameter(cell_tag, parameter_name):
    """
    Parse cell parameter value.

    Args:
        cell_tag: xml tag object
        parameter_name: strng

    Returns:
        string
    """
    for parameter_tag in cell_tag.iter(make_tag('p')):
        if parameter_tag.get('name') != parameter_name:
            continue
        return parameter_tag.text


def get_xml_path(logs_path, technology):
    """
    Get Nokia xml path.

    Args:
        logs_path: string
        technology: string

    Returns:
        string
    """
    for log in os.listdir(logs_path):
        if technology in log:
            return '{logs_path}/{log}'.format(logs_path=logs_path, log=log)
