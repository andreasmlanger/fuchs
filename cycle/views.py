from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from main.airtable_data import get_airtable
from main.maps import *
from main.utils import get_avatar
from .utils import *


@login_required
def cycle(request):
    return index(request)


def index(request):
    airtable = get_airtable('CYCLE')
    if request.method == 'POST':
        if request.POST.get('task') == 'mark_as_done':
            airtable.update(f"rec{request.POST.get('id')}", {'Status': 'Done'})
            return HttpResponse('OK')

        elif request.POST.get('task') == 'mark_as_undone':
            airtable.update(f"rec{request.POST.get('id')}", {'Status': None})
            return HttpResponse('OK')

        elif request.POST.get('task') == 'delete':
            airtable.delete(f"rec{request.POST.get('id')}")
            return HttpResponse('OK')

        # Download GPX
        elif 'Url' in request.headers:
            url = request.headers['Url']
            filename = request.headers['Filename']
            gpx = create_gpx_from_url(url, filename)
            return HttpResponse(gpx, content_type='application/gpx+xml')

        else:
            df = pd.read_csv(request.POST.get('map_url'))

            if request.POST.get('task') == 'fetch_map':
                m = create_map_html(df, icon='bicycle', width=340, height=200)
                return JsonResponse({'map': m})

            elif request.POST.get('task') == 'fetch_profile':
                b = create_bokeh_html(df, request.POST.get('title'), width=340)
                return JsonResponse({'bokeh': b})

    records = airtable.get_all(sort='Title')  # load all routes
    routes = []
    for r in records:
        if 'Map' not in r['fields']:
            continue
        filename = r['fields']['Map'][0]['filename'].split('.')[0]
        route = {'Id': r['id'][3:],  # remove 'rec' at beginning
                 'Title': r['fields']['Title'],
                 'Status': get_status_from_fields(r['fields']),
                 'Filename': filename,
                 'Url': r['fields']['Map'][0]['url'],
                 'Stats': get_stats_from_filename(filename)}
        routes.append(route)

    return render(request, 'cycle/index.html',
                  {'routes': routes, 'avatar': get_avatar(request)})


def open_route(_, route_id):
    airtable = get_airtable('CYCLE')
    record = airtable.get(f'rec{route_id}')
    m = create_map(record['fields']['Map'][0]['url'], icon='bicycle')
    file_name = record['fields']['Map'][0]['filename'].split('.')[0]
    arr = file_name.split('_')
    extra_html = '''
            <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
            <style>
                .body {
                    margin: 0;
                }
            </style>
            <title>
        ''' + f'{arr[-3]} ↑{arr[-2]} ↓{arr[-1]}' + '''
            </title>
        '''
    html = m.replace('</head>', f'{extra_html}</head>')

    response = HttpResponse(content_type='text/html')
    response.write(html)
    return response


def create_map(url, icon='bicycle', width=None, height=None):
    df = pd.read_csv(url)
    m = create_map_html(df, icon=icon, width=width, height=height)
    return m
