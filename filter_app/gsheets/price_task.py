import logging

from filter_app.gsheets.price_gatherer import gather_prices
from filter_app.gsheets.price_writer import write_prices, append_prices

import atexit
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler() # create scheduler
scheduler.start()   # start scheduler
atexit.register(lambda: scheduler.shutdown()) # shutdown scheduler when flask stops


# Schedules update_prices to be run every day
@scheduler.scheduled_job('cron', hour='18')  # every day of every year at 18hr
def update_prices():
    """
    Calls functions for adding gathered prices to the db and updating google spreadsheet with new prices
    """
    try:
        gather_prices()
        write_prices() # :TODO: rewrite with append instead of write
    except Exception as e:
        logging.exception(e, exc_info=True)
    finally:
        print(scheduler.print_jobs())
# scheduler.unschedule_job(job_function.job)
