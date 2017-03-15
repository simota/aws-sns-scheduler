import os
import sys
import time
import falcon
import shelve
import uuid
import signal
import pickle
from setproctitle import setproctitle
from apscheduler.scheduler import Scheduler
from apscheduler import events
from apscheduler.jobstores.shelve_store import ShelveJobStore


## api server
class NotficationsResource:

    def __init__(self, scheduler, store):
        self.scheduler = scheduler
        self.store = store

    def on_get(self, req, resp):
        notfication_id = self.store.add({})
        self.scheduler.add_job(my_job, '2017-03-15 14:15:30', args=[notfication_id])
        resp.body = 'get'

    def on_post(self, req, resp):
        pass

    def on_put(self, req, resp, notfication_id):
        pass

    def on_delete(self, req, resp, notfication_id):
        pass


## data store
class NotficationStore:

    def __init__(self, filename='notfication.db'):
        curdir = os.path.dirname(__file__)
        shelve_path = os.path.join(curdir, filename)
        self.db = shelve.open(shelve_path, 'c', pickle.HIGHEST_PROTOCOL)

    def add(self, notfication):
        notfication_id = uuid.uuid4()
        self.db[notfication_id] = notfication

    def remove(self, notfication_id):
        del self.db[notfication_id]

    def close(self):
        self.db.close()

    def find(self, notfication_id):
        if self.db.has_key(notfication_id):
            return self.db[notfication_id]
        return None


## scheduler
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

    def __init__(self, filename='scheduler.db'):
        curdir = os.path.dirname(__file__)
        store_path = os.path.join(curdir, filename)
        self.scheduler = Scheduler()
        self.scheduler.add_jobstore(ShelveJobStore(store_path), 'file')
        self.scheduler.add_listener(self.event_listener, events.EVENT_ALL)

    def start(self):
        self.scheduler.start()

    def add_job(self, job, date, args):
        job = self.scheduler.add_date_job(job, date, args)

    def jobs(self):
        return self.scheduler.get_jobs

    def remove_job(self):
        pass

    def shutdown(self):
        self.scheduler.shutdown()

    def event_listener(self, event):
        print EVENTS[str(event.code)]
        self.scheduler.print_jobs()


def my_job(text):
    print text


#    job = sched.add_interval_job(my_job, minutes=1, args=['hello'])
#    job = sched.add_date_job(job_function, '2013-08-05 23:47:05', ['hello'])

setproctitle('aws-sns-scheduler')
store = NotficationStore()
scheduler = MyScheduler()

def receive_signal(signum, stack):
    store.close()
    scheduler.shutdown()

signal.signal(signal.SIGUSR1, receive_signal)
signal.signal(signal.SIGUSR2, receive_signal)

scheduler.start()
api = falcon.API()
api.add_route('/notfications', NotficationsResource(scheduler, store))
api.add_route('/notfications/{notfication_id}', NotficationsResource(scheduler, store))
