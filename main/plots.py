from bokeh.events import DoubleTap
from bokeh.models.callbacks import CustomJS


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
    p.toolbar.logo = None
    p.toolbar_location = None
    p.js_on_event(DoubleTap, CustomJS(args=dict(p=p), code='p.reset.emit()'))  # reset plot after double-click
