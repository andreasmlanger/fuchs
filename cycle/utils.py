from xml.etree import ElementTree
import pandas as pd


def create_gpx_from_url(url, name):
    gpx_root = ElementTree.Element('gpx', version='1.1', xmlns='http://www.topografix.com/GPX/1/1')
    track = ElementTree.SubElement(gpx_root, 'trk')
    track_name = ElementTree.SubElement(track, 'name')
    track_name.text = name
    track_segment = ElementTree.SubElement(track, 'trkseg')

    df = pd.read_csv(url)
    latitudes = df['lat'].astype(str)
    longitudes = df['lon'].astype(str)
    elevations = df['elevation'].astype(int).astype(str)

    for lat, lon, ele in zip(latitudes, longitudes, elevations):
        track_point = ElementTree.SubElement(track_segment, 'trkpt', lat=lat, lon=lon)
        elevation = ElementTree.SubElement(track_point, 'ele')
        elevation.text = ele

    tree = ElementTree.ElementTree(gpx_root)
    ElementTree.indent(tree, '  ')

    gpx_str = ElementTree.tostring(gpx_root, encoding='utf-8')
    return gpx_str


def get_status_from_fields(fields):
    if 'Status' in fields:
        return fields['Status'].lower()
    return 'planned'


def get_stats_from_filename(x):
    arr = x.split('_')
    return f'{arr[-3]} ↑{arr[-2]} ↓{arr[-1]}'



