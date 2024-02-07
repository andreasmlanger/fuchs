from airtable import Airtable
from django.conf import settings
from datetime import datetime, timedelta
import json
import os
from mysite.settings import config


def get_airtable(app):
    base_id = config.get(f'AIRTABLE_BASE_ID_{app.upper()}')
    table_name = config.get(f'AIRTABLE_TABLE_NAME_{app.upper()}')
    token = config.get('AIRTABLE_TOKEN')
    return Airtable(base_id, table_name, token)


def fetch_json_data_from_media_folder(request, app, model, blog_id=None):
    """
    Opens json file from media folder and loads content, e.g. for Travel or Blog apps
    """
    app_media_folder = os.path.join(settings.MEDIA_ROOT, f'{app}')
    path_to_json_file = os.path.join(app_media_folder, 'data.json')
    data_instance = get_data_model_instance(model)  # get or create model instance
    json_missing = not os.path.isfile(path_to_json_file)
    if json_missing:
        os.makedirs(app_media_folder, exist_ok=True)
    json_is_obsolete = check_if_json_data_is_obsolete(request, data_instance)
    if json_missing or json_is_obsolete:
        update_travel_json(request, app, data_instance, get_airtable(app))
    with open(path_to_json_file, 'r') as f:
        data = json.load(f)
    if blog_id:
        return [d for d in data if d['Id'] == blog_id]
    return data


def check_if_json_data_is_obsolete(request, data_instance):
    """
    Airtable Free Tier only allows 1000 API requests per month = ~30 per day
    Attachment URLs remain unchanged for at least 1 hour, then they become obsolete
    """
    return datetime.now() - get_last_update_time(request, data_instance) > timedelta(hours=1)


def get_data_model_instance(model):
    if len(model.objects.all()) == 0:
        model.objects.create()  # create instance if it does not yet exist
    return model.objects.get()


def is_local(request):
    return request.get_host() in ('localhost', '127.0.0.1', '127.0.0.1:8000')


def get_last_update_time(request, instance):
    return instance.updated_at_local if is_local(request) else instance.updated_at_remote


def set_last_update_time(request, instance):
    if is_local(request):
        instance.updated_at_local = datetime.now()
    else:
        instance.updated_at_remote = datetime.now()
    instance.save()


def update_travel_json(request, app, data_instance, airtable):
    """
    Fetches data from Travel or Blog Airtable including URLs to maps
    Saves it remotely as json
    """
    sort = 'Date' if app == 'travel' else '-Date'  # sort descending/ascending depending on app
    records = airtable.get_all(sort=sort)
    data = []
    for r in records:
        d = {'Id': r['id'][3:],  # removes 'rec' at the beginning
             'Title': r['fields']['Title'],
             'Date': r['fields']['Date'],
             'Tags': r['fields']['Tags'],
             'Content': r['fields']['Content'] if 'Content' in r['fields'].keys() else ''}
        if 'Attachments' in r['fields'].keys():
            attachments = {}
            for a in r['fields']['Attachments']:
                attachments[a['filename']] = a['url']
            d['Attachments'] = attachments
        if 'Map' in r['fields'].keys():
            d['Map'] = r['fields']['Map'][0]['filename'].split('.')[0]  # remove '.csv'
            d['MapURL'] = r['fields']['Map'][0]['url']
        data.append(d)
    file_path = os.path.join(settings.MEDIA_ROOT, f'{app}/data.json')
    with open(file_path, 'w') as fp:
        json.dump(data, fp)
    set_last_update_time(request, data_instance)
    print(f'{app.capitalize()} JSON successfully updated!')


def format_content(data):
    """
    Formats the content of a post (blog & travel apps)
    """
    for d in data:
        if 'Content' in d:
            content = d['Content'].split('\n')
            for i in range(len(content)):
                if content[i].startswith('{'):
                    stripped_content = content[i].lstrip('{').rstrip('}')
                    if stripped_content.startswith('https://'):
                        # YouTube or Vimeo video
                        content[i] = {'vid': stripped_content}
                    else:
                        if stripped_content.lower().endswith('mp3'):
                            # audio
                            content[i] = {'aud': d['Attachments'][stripped_content]}
                        else:
                            # image
                            if '|' in stripped_content:
                                stripped_content, width = stripped_content.split('|')
                            else:
                                width = '300px'
                            content[i] = {'img': d['Attachments'][stripped_content], 'width': width}
                else:
                    # simple paragraph
                    content[i] = {'p': content[i]}
            d['Content'] = content
    return data
