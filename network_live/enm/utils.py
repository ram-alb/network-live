import re


def parse_fdn(fdn, mo_type):
    """
    Parse the MO value from a Full Distinguished Name (FDN).

    Args:
        fdn (str): the FDN string to parse
        mo_type (str): the type of MO to parse from the FDN (e.g. 'SubNetwork')

    Returns:
        str: the value of the specified MO in the FDN string
    """
    re_patterns = {
        'SubNetwork': ',SubNetwork=[^,]*',
        'MeContext': 'MeContext=[^,]*',
        'ManagedElement': 'ManagedElement=[^,]*',
        'NRSectorCarrier': 'NRSectorCarrier=.*',
        'NRCellDU': 'NRCellDU=.*',
        'EUtranCellFDD': 'EUtranCellFDD=[^,]*',
        'IubLink': 'IubLink=.*',
        'UtranCell': 'UtranCell=.*',
        'GsmSector': 'GsmSector=.*',
        'GeranCell': 'GeranCell=.*',
        'ChannelGroupCell': 'GeranCell=[^,]*',
    }

    mo_value_index = -1
    if mo_type == 'MeContext':
        try:
            mo = re.search(re_patterns['MeContext'], fdn).group()
        except AttributeError:
            mo = re.search(re_patterns['ManagedElement'], fdn).group()
    else:
        mo = re.search(re_patterns[mo_type], fdn).group()

    return mo.split('=')[mo_value_index]


def parse_node_parameter(enm_node_data, node_type):
    """
    Parse the node parameters.

    Parsing is done from a tuple of ElementGroup objects for a
    specific node type.

    Args:
        enm_node_data (tuple): a tuple of ElementGroup objects to parse
        node_type (str): the type of node to parse parameters for

    Returns:
        dict: a dictionary of node parameter names and values
    """
    attr_delimeter = ' : '
    attr_value_index = -1
    node_parameters = {}
    for element in enm_node_data:
        element_val = element.value()
        if 'FDN' in element_val:
            node_name = parse_fdn(element_val, node_type)
        elif attr_delimeter in element_val:
            parameter_val = element_val.split(attr_delimeter)[attr_value_index]
            node_parameters[node_name] = parameter_val

    return node_parameters


def get_ip(ip_string):
    """
    Extract an IP address from a string.

    Args:
        ip_string (str): the string to extract the IP address from

    Returns:
        str: the extracted IP address, or None if no IP address was found
    """
    ip_re_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    try:
        ip_address = re.search(ip_re_pattern, ip_string).group()
    except AttributeError:
        ip_address = None
    return ip_address


def parse_bbu_ips(enm_ip_data, router_type):
    """
    Parse the BBU IP addresses from a tuple of ElementGroup objects.

    Args:
        enm_ip_data (tuple): a list of ElementGroup objects to parse
        router_type (str): a router type, for example (oam, iub)

    Returns:
        dict: a dictionary of BBU names and IP addresses
    """
    node_ips = {}
    router = False
    for element in enm_ip_data:
        element_val = element.value()
        if 'FDN' in element_val and router_type in element_val.lower():
            name = parse_fdn(element_val, 'MeContext')
            router = True
        elif ' : ' in element_val and router:
            node_ips[name] = get_ip(element_val)
            router = False
    return node_ips
