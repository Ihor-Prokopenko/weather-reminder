from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler

from WRapi.models import Period
from WRapi.notificator import send_mails

TEST_HOUR = 18
TEST_MINUTE = 58

schedule = BackgroundScheduler()


def add_jobs(period, func):
    hours = period.get_hours_list()

    for hour in hours:
        job_id = f"{hour}h interval mail"
        trigger = 'cron'
        # if schedule.get_job(job_id):
        #     schedule.remove_job(job_id)
        # try:
        #     schedule.add_job(func, trigger, hour=hour, args=[period.interval],
        #                      id=job_id)
        # except ConflictingIdError:
        #     schedule.modify_job(func, trigger, hour=hour, args=[period.interval],
        #                         id=job_id)
        if schedule.get_job(job_id):
            schedule.remove_job(job_id)
        try:
            schedule.add_job(func, trigger, hour=TEST_HOUR, minute=TEST_MINUTE, second=hour, args=[period.interval],
                             id=job_id)
        except ConflictingIdError:
            schedule.modify_job(func, trigger, hour=TEST_HOUR, minute=TEST_MINUTE, second=hour, args=[period.interval],
                                id=job_id)


def create_jobs():
    if schedule and schedule.running:
        schedule.shutdown()

    schedule.print_jobs()

    print("Creating jobs...")

    periods = Period.objects.all().order_by('interval')
    for period in periods:
        add_jobs(period, send_mails)
    print("Jobs created!")

    schedule.start()
    print("Schedule started!")
