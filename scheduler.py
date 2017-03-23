from apscheduler.scheduler import Scheduler
from apscheduler import events
from apscheduler.jobstores.sqlalchemy_store import SQLAlchemyJobStore

class MyScheduler:

    EVENTS = {
        '1': 'EVENT_SCHEDULER_START',
        '2': 'EVENT_SCHEDULER_SHUTDOWN',
        '3': 'EVENT_JOBSTORE_ADDED',
        '4': 'EVENT_JOBSTORE_REMOVED',
        '5': 'EVENT_JOBSTORE_JOB_ADDED',
        '32': 'EVENT_JOBSTORE_JOB_REMOVED',
        '64': 'EVENT_JOB_EXECUTED',
        '128': 'EVENT_JOB_ERROR',
        '256': 'EVENT_JOB_MISSED'
        }

    def __init__(self, db_path='sqlite:///scheduler.db'):
        self.scheduler = Scheduler()
        self.scheduler.add_jobstore(SQLAlchemyJobStore(url=db_path), 'default')
        self.scheduler.add_listener(self.event_listener, events.EVENT_ALL)

    def start(self):
        self.scheduler.start()

    def add_job(self, job, date, args):
        job = self.scheduler.add_date_job(job, date, args)
        print job

    def jobs(self):
        return self.scheduler.get_jobs()

    def remove_job(self, notfication_id):
        for job in self.jobs():
            if job.args[0] == notfication_id:
                self.scheduler.unschedule_job(job)
                return True
        return False

    def shutdown(self):
        self.scheduler.shutdown()

    def event_listener(self, event):
        print self.EVENTS[str(event.code)]
        self.scheduler.print_jobs()


def create_scheduler():
    return MyScheduler()
