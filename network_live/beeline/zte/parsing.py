import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import pandas as pd
from datetime import date
from network_live.sql import get_atoll_data
from point_in_region import find_region_by_coordinates
import os 

def extract_attributes(element: Element, namespace: dict) -> dict:
    """
    Args:
        element(Element): XML-element
        namespace(dict): namespase for work with XML
    
    Returns:
        dict: Dictionary of attributes with values
    """
    attributes = element.find("ns:attributes", namespace)
    if attributes is not None:
        return {child.tag.split("}")[1]: child.text for child in attributes}
    return {}

def extract_mo_data(moc_type, root, namespace):
    data = []
    for mo in root.findall(f".//ns:mo[@moc='{moc_type}']", namespace):
        mo_data = extract_attributes(mo, namespace)
        mo_data["moc"] = moc_type
        data.append(mo_data)
    return pd.DataFrame(data)

def parse_wcdma_parameters(xml_file_path):
    if os.path.isdir(xml_file_path):
        raise Exception("Нет логов")
    
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    namespace = {"ns": "http://www.zte.com/specs/nrm"}
    mo_types = ["UUtranCellFDD", "UIubLink"]
    
    cell_data = get_atoll_data()
    df_data_3g = cell_data['WCDMA']
    df_data_3g.columns = ["UTRANCELL", "height"]
    optimized_dataframes = {moc: extract_mo_data(moc, root, namespace) for moc in mo_types}
    
    df_wcdma_cells = optimized_dataframes["UUtranCellFDD"]
    df_wcdma_cells.rename(columns={"userLabel": "UTRANCELL"}, inplace=True)
    df_wcdma_cells["LAC"] = df_wcdma_cells["refULocationArea"].str.extract(r"ULocationArea=(\d+)").astype(int)
    df_wcdma_cells["RAC"] = df_wcdma_cells["refURoutingArea"].str.extract(r"URoutingArea=(\d+)").astype(int)
    df_wcdma_cells["SAC"] = df_wcdma_cells["refUServiceArea"].str.extract(r"UServiceArea=(\d+)").astype(int)
    df_wcdma_cells["IubLink"] = df_wcdma_cells["refUIubLink"].str.extract(r"UIubLink=(\d+)").astype(str)
    
    df_wcdma_base_station = optimized_dataframes["UIubLink"]
    df_wcdma_base_station["moId"] = df_wcdma_base_station["moId"].astype(str)
    df_wcdma_base_station.rename(columns={"userLabel": "Sitename"}, inplace=True)

    df_merge_wcdma = df_wcdma_cells.merge(df_wcdma_base_station, left_on="IubLink", right_on="moId", how="left")

    df_merge_wcdma = df_merge_wcdma.merge(df_data_3g, on = "UTRANCELL", how = "left")
    
    df_merge_wcdma["region"]= df_merge_wcdma.apply(lambda row: find_region_by_coordinates((row["longitude"], row["latitude"])), axis=1)
    df_merge_wcdma["cellState"] = df_merge_wcdma.apply(lambda row: "UNLOCKED" if row["AdmState"] == 'Unblock' else "LOCKED", axis=1)
    
    df_merge_wcdma = df_merge_wcdma.applymap(lambda x: None if pd.isna(x) else x)
    
    df_merge_wcdma = df_merge_wcdma.assign(
        Operator = "Beeline", 
        RNCID = None,
        RNCNAME = None,
        URALIST = None,
        Vendor = "ZTE",
        OSS = "Beeline ZTE", 
        insertdate=date.today(),
        QRXLEVMIN = None,
        QQUALMIN = None,
        IPADDRESS = None,
        MOCNCELLPROFILE= None)
    
    df_result_wcdma = df_merge_wcdma[[
        "Operator",
        "RNCID",
        "RNCNAME",
        "Sitename",
        "UTRANCELL",
        "localCellId",
        "cId",
        "uarfcnDl",
        "uarfcnUl",
        "primaryScramblingCode",
        "LAC",
        "RAC",
        "SAC",
        "URALIST",
        "primaryCpichPower",
        "maximumTransmissionPower",
        "QRXLEVMIN",
        "QQUALMIN",
        "IubLink",
        "MOCNCELLPROFILE",
        "cellState",
        "IPADDRESS",
        "Vendor",
        "OSS",
        "offsetAngle",                                
        "height",  
        "longitude",
        "latitude",
        "insertdate",
        "region"
    ]]
    cells_3g = [tuple(None if pd.isna(value) else value for value in row) for row in df_result_wcdma.to_numpy()]
    return cells_3g

def get_earfcn(in_mhz):
    if 1800 > in_mhz > 790:
        return 6200
    elif 2100 > in_mhz > 1800:
        return 1302
    elif in_mhz > 2100:
        return 125 

def parse_gsm_parameters(xml_file_path):
    if os.path.isdir(xml_file_path):
        raise Exception("Нет лог файлов")
    
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    namespace = {"ns": "http://www.zte.com/specs/nrm"}

    mo_types = ["GGsmCell", "GBtsSiteManager", "GLocationArea", "GTrx", "UPlmnSpecFunction"]
    cell_data = get_atoll_data()
    df_data_2g = cell_data['GSM']
    df_data_2g.columns=["cellName", "height", "bsc_name"]
    optimized_dataframes = {moc: extract_mo_data(moc, root, namespace) for moc in mo_types}

    df_gsm_cells = optimized_dataframes["GGsmCell"]
    df_gsm_cells.rename(columns={"userLabel": "cellName"}, inplace=True)
    df_gsm_base_station = optimized_dataframes["GBtsSiteManager"]
    df_gsm_base_station.rename(columns={"userLabel": "siteName"}, inplace=True)
    df_gsm_lac = optimized_dataframes["GLocationArea"]
    df_gsm_trx = optimized_dataframes["GTrx"]
    df_gsm_trx.rename(columns={"userLabel":"cellName"}, inplace=True)
    df_gsm_trx_filtered = df_gsm_trx[df_gsm_trx["BCCHMARK"] == '0']
    tchfreqs = (
        df_gsm_trx_filtered.groupby("cellName")["arfcn"]
        .apply(lambda x: ", ".join(x.astype(str)))
        .reset_index()
        .rename(columns={"arfcn": "tchfreqs"})
    )
 
    df_gsm_cells['SiteManager'] = df_gsm_cells["MOI"].str.extract(r"GBtsSiteManager=(\d+)").astype(str)
    df_gsm_cells['LACRef'] = df_gsm_cells["refGLocationArea"].str.extract(r"GLocationArea=(\d+)").astype(str)

    df_gsm_base_station["moId"] = df_gsm_base_station["moId"].astype(str)
    df_gsm_lac["moId"] = df_gsm_lac["moId"].astype(str)
    df_merge_gsm = df_gsm_cells.merge(df_gsm_base_station, left_on="SiteManager", right_on="moId", how="left")
    df_merge_gsm = df_merge_gsm.merge(df_gsm_lac, left_on="LACRef", right_on="moId", how="left")
    df_merge_gsm = df_merge_gsm.merge(tchfreqs, on="cellName", how="left")
    df_merge_gsm = df_merge_gsm.merge(df_data_2g, on="cellName", how = "left")
    df_merge_gsm["region"] = df_merge_gsm.apply(lambda row: find_region_by_coordinates((row["Longitude"], row["Latitude"])), axis=1)
    df_merge_gsm["cellState"] = df_merge_gsm.apply(lambda row: "ACTIVE" if row["OperState"] == 'Unblock' else "HALTED", axis=1)
    df_merge_gsm = df_merge_gsm.applymap(lambda x: None if pd.isna(x) else x)
    df_merge_gsm = df_merge_gsm.assign(
        Operator="Beeline", 
        BSCID= None,
        Vendor="ZTE",
        OSS="Beeline ZTE", 
        insertdate=date.today(),
        HSN = None,
        MAIO = None)
    df_result_gsm = df_merge_gsm[[
                                "Operator",
                                "BSCID",
                                "bsc_name",
                                "siteName",
                                "cellName", 
                                "bcc", 
                                "ncc", 
                                "lac", 
                                "cellIdentity", 
                                "bcchFrequency",
                                "HSN",
                                "MAIO", 
                                "tchfreqs", 
                                "cellState",
                                "Vendor",
                                "OSS",
                                "offsetAngle",
                                "height",  
                                "Longitude", 
                                "Latitude",
                                "insertdate", 
                                "region"]]
    


    cells_2g = [tuple(None if pd.isna(value) else value for value in row) for row in df_result_gsm.to_numpy()]
    return cells_2g


def parce_lte_parameters(csv_file_path, ip_file_path):
    cell_data = get_atoll_data()
    df_data_4g = cell_data["LTE"]
    df_data_4g.columns=["userLabel", "height"]
    df_lte = pd.read_csv(csv_file_path)
    df_filtered_lte = df_lte[[
        "ManagedElement",
        "userLabel",
        "tac",
        "pci",
        "cellLocalId",
        "earfcnDl",
        "earfcnUl",
        "adminState",
        "latitude",
        "longitude",
        "offsetAngle",
        "ueAbsoluteSignalThr",
        "cellRadius",
    ]]

    df_ip = pd.read_csv(ip_file_path)
    df_ip["moId"] = df_ip["moId"].astype(str)
    df_ip = df_ip[df_ip["moId"] == '2']
    df_merge_lte = df_filtered_lte.merge(df_ip, on="ManagedElement", how = "left")

    df_merge_lte["region"] = df_merge_lte.apply(lambda row: find_region_by_coordinates((row["longitude"], row["latitude"])), axis=1)
    df_merge_lte["cellState"] = df_merge_lte.apply(lambda row: "UNLOCKED" if row["adminState"] == 0 else "LOCKED", axis=1)
    df_merge_lte["ManagedElement"] = df_merge_lte["ManagedElement"].astype(int)
    df_merge_lte["cellLocalId"] = df_merge_lte["cellLocalId"].astype(int)
    df_merge_lte["eci"] = df_merge_lte.apply(lambda row: row["ManagedElement"] * 256 + row["cellLocalId"], axis=1)
    df_merge_lte["EARFCN"] = df_merge_lte.apply(lambda row: get_earfcn(row["earfcnDl"]), axis = 1)
    df_merge_lte = df_merge_lte.assign(
        SUBNETWORK = "Beeline",
        Vendor = "ZTE",
        OSS = "Beeline ZTE",
        insertdate = date.today(),
        SHARINGTYPE = None,
        RACHROOTSEQUENCE = None,
        TXNUMBER = None,
        RXNUMBER = None,
        Sitename = ""
    )

    df_merge_lte = df_merge_lte.merge(df_data_4g, on= "userLabel", how="left")    
    df_merge_lte = df_merge_lte.applymap(lambda x: None if pd.isna(x) else x)

    df_result_lte = df_merge_lte[[
        "SUBNETWORK",
        "ManagedElement",
        "ManagedElement", # Sitename
        "userLabel",
        "tac",
        "cellLocalId",
        "eci",
        "EARFCN",
        "ueAbsoluteSignalThr",
        "cellState",
        "RACHROOTSEQUENCE",
        "pci",
        "cellRadius",
        "Vendor",
        "ipAddress",
        "OSS",
        "offsetAngle",
        "height",
        "longitude",
        "latitude",
        "insertdate",
        "SHARINGTYPE",
        "region",
        "TXNUMBER",
        "RXNUMBER"
        ]]
    cells_4g = [tuple(None if pd.isna(value) else value for value in row) for row in df_result_lte.to_numpy()]
    return cells_4g
