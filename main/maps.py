from bokeh.embed import file_html
from bokeh.events import DoubleTap
from bokeh.models import HoverTool
from bokeh.models.callbacks import CustomJS
from bokeh.plotting import figure
from bokeh.resources import CDN
import folium
from folium.plugins import Fullscreen
import numpy as np
import pandas as pd
import os
from mysite.settings import config
from .utils import round_down_to_next_100, round_up_to_next_100


MAPS_DIR = os.path.join('travel', 'maps')  # directory where maps are stored
COLOR = '#1381fa'  # line color on maps
API_KEY = config.get('STADIA_API_KEY')  # https://client.stadiamaps.com/dashboard/#/property/15531/


def create_map_html(df, icon='bicycle', width=None, height=None):
    # Create new Folium map
    f = folium.Figure(width=width, height=height)
    m = folium.Map(zoom_control=False).add_to(f)

    # Use Stadiamaps Terrain tile layer
    tile_layer_url = 'https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}.jpg?api_key=' + API_KEY
    tile_layer = folium.TileLayer(tile_layer_url, attr='©Fuchs')
    tile_layer.add_to(m)

    # Add a polyline to the map using the GPS track points
    folium.PolyLine(locations=df[['lat', 'lon']].values.tolist(), color=COLOR).add_to(m)

    # Find bounds and ideal zoom
    m.fit_bounds(get_bounds(df))

    # Add start and end markers
    def create_icon(color):
        return folium.Icon(color=color, icon_color='white', icon=icon, prefix='fa')

    def create_popup(text):
        return folium.Popup(f'<span style="font-size: 16px">{text}</span>', max_width=400)

    folium.Marker(df[['lat', 'lon']].iloc[0], popup=create_popup('Start'), icon=create_icon('green')).add_to(m)
    folium.Marker(df[['lat', 'lon']].iloc[-1], popup=create_popup('End'), icon=create_icon('red')).add_to(m)

    if width and height:
        Fullscreen().add_to(m)  # add full-screen option if map with width and height
        # noinspection PyProtectedMember
        return m._repr_html_()

    return m.get_root().render()


def create_bokeh_html(df, file_name, width=300, height=200):
    if 'elevation' not in df.columns:
        return ''  # if no elevation saved in csv file, then it's not a bicycle route, so no elevation profile is shown

    # Create figure
    p = figure(width=width, height=height, tools='box_zoom, reset')

    # Reduce number of points in bokeh plot to improve loading performance
    df = reduce_number_of_points_in_profile(df)

    # Set ranges
    p.x_range.start = 0
    p.x_range.end = df['distance'].iloc[-1]
    y_min = min(0, round_down_to_next_100(df['elevation'].min()))
    y_max = round_up_to_next_100(df['elevation'].max() + 50)
    p.y_range.start = y_min
    p.y_range.end = y_max

    # Plot glyphs
    line = p.line(df['distance'], df['elevation'], line_width=3, color=COLOR)
    p.varea(x=df['distance'], y1=df['elevation'], y2=y_min, fill_color=COLOR, fill_alpha=0.1)
    p.circle(df['distance'].iloc[0], df['elevation'].iloc[0], color='#72b026', size=8)
    p.circle(df['distance'].iloc[-1], df['elevation'].iloc[-1], color='#d63e2a', size=8)

    # Add title with metadata from file name
    arr = file_name.split('_')
    p.title.text = f'{arr[-3]} ↑{arr[-2]} ↓{arr[-1]}'

    # Format
    format_bokeh_plot(p)

    # Add hover
    p.add_tools(HoverTool(renderers=[line], tooltips=[('', '@y{0} m')], mode='vline', attachment='above'))

    bokeh_html = file_html(p, CDN, 'bokeh')
    return bokeh_html


def get_bounds(df):
    min_lat, max_lat = df['lat'].min(), df['lat'].max()
    min_lon, max_lon = df['lon'].min(), df['lon'].max()
    border_lat = 0.1 * abs(min_lat - max_lat)
    border_lon = 0.1 * abs(min_lon - max_lon)
    return [(min_lat - border_lat, min_lon - border_lon), (max_lat + border_lat, max_lon + border_lon)]


def reduce_number_of_points_in_profile(df):
    if len(df) > 200:
        new_distance = np.linspace(0, df['distance'].iloc[-1], 200)
        interpolated_elevation = np.interp(new_distance, df['distance'], df['elevation'])
        df = pd.DataFrame({'distance': new_distance, 'elevation': interpolated_elevation})
    return df


def format_bokeh_plot(p):
    font = 'Segoe UI'
    p.xaxis.major_label_overrides = {0: 'km'}
    p.yaxis.major_label_overrides = {0: 'm'}
    p.xaxis.axis_label_text_font = font
    p.yaxis.axis_label_text_font = font
    p.xaxis.axis_label_text_font_style = 'normal'
    p.yaxis.axis_label_text_font_style = 'normal'
    p.xaxis.major_label_text_font = font
    p.yaxis.major_label_text_font = font
    p.title.text_font_style = 'normal'
    p.title.text_font = font
    p.xaxis.axis_label_text_font_size = '13pt'
    p.yaxis.axis_label_text_font_size = '13pt'
    p.xaxis.major_label_text_font_size = '12pt'
    p.yaxis.major_label_text_font_size = '12pt'
    p.toolbar.logo = None
    p.background_fill_color = None
    p.border_fill_color = None
    p.toolbar_location = None
    p.js_on_event(DoubleTap, CustomJS(args=dict(p=p), code='p.reset.emit()'))
