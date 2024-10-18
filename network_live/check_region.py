import geopandas as gpd
from shapely.geometry import Point
import os


def read_udrs():
    map_paths = {
        'Astana-city': 'maps/astana-city/astana-city.shp',
        'Akmola-obl': 'maps/akmola-obl/akmola-obl.shp',
        'Almaty-city': 'maps/almaty-city/almaty-city.shp',
        'Almaty-obl': 'maps/almaty-obl/almaty-obl.shp',
        'Aktobe-region': 'maps/aktobe-obl/aktobe-obl.shp',
        'Atyrau-region': 'maps/atyrau-obl/atyrau-obl.shp',
        'Karaganda-region': 'maps/karaganda-obl/karaganda-obl.shp',
        'Kostanay-region': 'maps/kostanay-obl/kostanay-obl.shp',
        'Kyzylorda-region': 'maps/kyzylorda-obl/kyzylorda-obl.shp',
        'Mangystau-region': 'maps/mangystau-obl/mangystau-obl-polygon.shp',
        'Pavlodar-region': 'maps/pavlodar-obl/pavlodar-obl.shp',
        'North-Kazakhstan': 'maps/sko/sko.shp',
        'South-Kazakhstan': 'maps/uko/uko.shp',
        'East-Kazakhstan': 'maps/vko/vko.shp',
        'Zhambyl-region': 'maps/zhambyl-obl/zhambyl-obl.shp',
        'West-Kazakhstan': 'maps/zko/zko-polygon.shp',
        'Kazmin': 'maps/kazmin/Kazmin-polygon.shp',
    }

    return {
        region: gpd.read_file(path).geometry[0] for region, path in map_paths.items()
    }


def _define_region(cell_point, udrs):
    for region, udr in udrs.items():
        if cell_point.within(udr):
            return region


def add_region(cell, udrs):
    if cell['longitude']:
        cell_point = Point(cell['longitude'], cell['latitude'])
        cell['region'] = _define_region(cell_point, udrs)
    else:
        cell['region'] = None
    return cell
