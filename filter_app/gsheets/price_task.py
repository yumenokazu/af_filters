import logging
from datetime import datetime, timedelta

from filter_app.gsheets.price_gatherer import gather_prices
from filter_app.gsheets.price_writer import write_prices, append_prices

import atexit
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler() # create scheduler
scheduler.start()   # start scheduler
atexit.register(lambda: scheduler.shutdown()) # shutdown scheduler when flask stops


# Schedules update_prices to be run every day
@scheduler.scheduled_job('cron', id="upd_price", minute="22", misfire_grace_time=3600, coalesce=True, max_instances=3)  # every day of every year at 18hr
def update_prices():
    """
    Calls functions for adding gathered prices to the db and updating google spreadsheet with new prices
    """
    try:
        # :TODO: add check whether league is on
        gather_prices()
        write_prices() # :TODO: rewrite with append instead of write
    except Exception as e:
        # :TODO: add event listener for retry logic! https://apscheduler.readthedocs.io/en/v2.1.2/index.html#scheduler-events
        # :TODO: add notifications?
        logging.exception(e, exc_info=True)
        for job in scheduler.get_jobs():
            if job.id == "upd_price":
                job.modify(next_run_time=datetime.now() + timedelta(minutes = 10))
    finally:
        print(scheduler.print_jobs())
