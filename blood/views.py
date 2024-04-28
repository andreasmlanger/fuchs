from bokeh.embed import file_html
from bokeh.layouts import column
from bokeh.palettes import inferno, viridis
from bokeh.plotting import figure
from bokeh.resources import CDN
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from main.plots import format_bokeh_plot
from main.utils import get_avatar
from .models import Blood

TOOLS = 'wheel_zoom, box_zoom, reset'


@login_required
def index(request):
    if request.POST.get('systolic'):
        new_blood_reading = Blood(user=request.user,
                                  systolic=request.POST.get('systolic'),
                                  diastolic=request.POST.get('diastolic'),
                                  pulse=request.POST.get('pulse')
                                  )
        new_blood_reading.save()

    blood_readings = request.user.blood.all().order_by('created_at')

    x = [b.created_at for b in blood_readings]
    y = [(b.systolic, b.diastolic, b.pulse) for b in blood_readings]

    # Create bokeh plot
    colors = (inferno(9)[3], inferno(9)[6], viridis(9)[4])
    labels = ('Systolic (mm)', 'Diastolic (mm)', 'Pulse')
    y_ideal = (115, 75)

    p1 = figure(height=280, width=900, x_axis_type='datetime', y_axis_label='mm Hg', tools=TOOLS)
    p2 = figure(height=180, width=900, x_axis_type='datetime', y_axis_label='Pulse', tools=TOOLS)

    if len(x) > 0:
        delta_x = max(x) - min(x)
        p1.x_range.start = min(x) - 0.05 * delta_x
        p1.x_range.end = max(x) + 0.05 * delta_x

        for i in range(2):
            p1.rect(x=min(x) + 0.5 * delta_x, y=y_ideal[i], width=delta_x * 1.1, height=10, fill_color='#3BB273',
                    fill_alpha=0.1, line_color=None)
            p1.line(x, [v[i] for v in y], line_width=3, color=colors[i], alpha=0.5, legend_label=labels[i])
            p1.scatter(x, [v[i] for v in y], size=8, color=colors[i], legend_label=labels[i])

        p2.line(x, [v[2] for v in y], line_width=3, color=colors[2], alpha=0.5, legend_label=labels[2])
        p2.scatter(x, [v[2] for v in y], size=8, color=colors[2], legend_label=labels[2])

        format_bokeh_plot(p1)
        format_bokeh_plot(p2)

    p = column(p1, p2)
    p.sizing_mode = 'stretch_width'
    bokeh_html = file_html(p, CDN, 'bokeh')

    if request.POST.get('systolic'):
        return JsonResponse({'bokeh_html': bokeh_html})
    return render(request, 'blood/index.html', {'bokeh_html': bokeh_html, 'avatar': get_avatar(request)})
