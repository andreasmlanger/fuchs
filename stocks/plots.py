from bokeh.events import DoubleTap
from bokeh.models import DatetimeTickFormatter
from bokeh.models.callbacks import CustomJS
from bokeh.palettes import Viridis256, Plasma256
from bokeh.plotting import figure
import numpy as np
import itertools


def create_individual_portfolio_plot(df, pf):
    p = figure(height=420, tools='box_zoom, reset')
    colors = itertools.cycle((Viridis256 + Plasma256[::-1])[::512 // len(pf)])

    for symbol, name in zip(pf.index, pf['name']):
        p.line(df.index.values, df[symbol], line_width=3, color=next(colors), alpha=0.8, muted_alpha=0.2,
               legend_label=name)

    format_bokeh_plot(p)  # Format font, font size & legend
    p.xaxis.formatter = DatetimeTickFormatter()
    return p


def create_aggregated_portfolio_plot(df, df2):
    p = figure(height=420, tools='box_zoom, reset')
    colors = itertools.cycle(['#e65162', '#4a536b'])

    for header in df2.columns:
        p.line(df.index.values, df2[header], line_width=3, color=next(colors), alpha=0.8, muted_alpha=0.2,
               legend_label=header)

    format_bokeh_plot(p)  # Format font, font size & legend
    p.xaxis.formatter = DatetimeTickFormatter()
    return p


def create_individual_watchlist_plot(df, pf, df_90):
    p = figure(height=420, tools='box_zoom, reset')
    colors = itertools.cycle((Viridis256 + Plasma256[::-1])[::512 // len(pf)])

    x = df.index.values
    for symbol, name in zip(pf.index, pf['name']):
        color = next(colors)
        y = df[symbol]
        p.line(x, y, line_width=3, color=color, alpha=0.8, muted_alpha=0.2, legend_label=name)
        y2 = df_90[symbol]
        p.line(x, y2, line_width=2, color=color, alpha=0.4, muted_alpha=0, legend_label=name)

    format_bokeh_plot(p)  # Format font, font size & legend
    p.xaxis.formatter = DatetimeTickFormatter()
    return p


def create_watchlist_volatility_plot(df_vo, pf):
    p = figure(height=420, tools='box_zoom, reset')
    colors = itertools.cycle((Viridis256 + Plasma256[::-1])[::512 // len(pf)])

    for stock in df_vo.columns:
        y = df_vo[stock][df_vo[stock] != 0]
        hist, edges = np.histogram(y, density=True, range=(-10, 10), bins=50)
        p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color=next(colors), alpha=0.4,
               muted_alpha=0.1, legend_label=pf.loc[stock, 'name'])

    format_bokeh_plot(p)  # Format font, font size & legend
    p.y_range.start = 0
    return p


def format_bokeh_plot(p):
    p.background_fill_color = '#eee'
    p.border_fill_color = '#eee'
    p.xaxis.axis_label_text_font = 'Segoe UI'
    p.yaxis.axis_label_text_font = 'Segoe UI'
    p.xaxis.axis_label_text_font_style = 'normal'
    p.yaxis.axis_label_text_font_style = 'normal'
    p.xaxis.axis_label_text_font_size = '13pt'
    p.yaxis.axis_label_text_font_size = '13pt'
    p.yaxis.axis_label_standoff = 10
    p.xaxis.major_label_text_font = 'Segoe UI'
    p.yaxis.major_label_text_font = 'Segoe UI'
    p.xaxis.major_label_text_font_size = '12pt'
    p.yaxis.major_label_text_font_size = '12pt'
    p.legend.label_text_font = 'Segoe UI'
    p.legend.label_text_font_size = '12pt'
    p.legend.background_fill_alpha = 0.8
    p.legend.background_fill_color = '#eee'
    p.legend.click_policy = 'mute'  # hide
    p.legend.location = 'top_left'
    p.sizing_mode = 'stretch_width'
    p.toolbar.logo = None
    p.toolbar_location = None
    p.js_on_event(DoubleTap, CustomJS(args=dict(p=p), code='p.reset.emit()'))  # reset plot after double-click
