from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import traceback
from main.emails import send_error_email
from main.utils import date_to_string, update_notification
from events.views import check_for_new_events, filter_and_save_new_events, send_events_email
from quotes.views import send_daily_quotes_email
from scrape.views import scrape
from stocks.views import check_stocks
from vocabulary.views import send_vocab_notification_email, vocab_ready_for_study


JOBS = {1: ['scrape', 'vocabulary', 'quotes', 'stocks'],
        2: ['events']}

EVENT_CITY = 'München'  # limit automatic event search to Munich


def run_scheduling(job):
    if job not in JOBS.keys():
        return ['AWAKE']
    status = []
    now = datetime.now()
    for app in JOBS[job]:
        city_events = check_for_new_events(EVENT_CITY) if app == 'events' else {}  # scrape for events in EVENT_CITY
        for user in get_user_model().objects.all():
            new_events = filter_and_save_new_events(user, city_events) if user.profile.city == EVENT_CITY else []
            if not user.notifications.get(app=app).email:
                status.append([user.username, app, 'INACTIVE', 'N/A'])
            elif now > user.notifications.get(app=app).due:
                try:
                    if app == 'events' and len(new_events) > 0:
                        send_events_email(user, new_events)
                    elif app == 'quotes':
                        send_daily_quotes_email(user)
                    elif app == 'scrape':
                        scrape(user, 'kleinanzeigen', 'urlaubspiraten')
                    elif app == 'stocks':
                        check_stocks(user)
                    elif app == 'vocabulary' and vocab_ready_for_study(user):
                        send_vocab_notification_email(user)
                    status.append([user.username, app, 'OK', date_to_string(user.notifications.get(app=app).due)])
                except Exception as ex:
                    print(ex)
                    send_error_email(traceback.format_exc())
                    update_notification(user, app, time_delta=timedelta(hours=24))  # allow 1 day to fix error
                    status.append([user.username, app, 'ERROR', date_to_string(user.notifications.get(app=app).due)])
            else:
                status.append([user.username, app, 'IDLE', date_to_string(user.notifications.get(app=app).due)])
    return status
