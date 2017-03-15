import os
import sys
import time
import falcon
import uuid
import signal
from sqlalchemy import create_engine, MetaData, Column, Integer, String, Text, DATETIME
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from setproctitle import setproctitle
from apscheduler.scheduler import Scheduler
from apscheduler import events
from apscheduler.jobstores.sqlalchemy_store import SQLAlchemyJobStore

## database
engine = create_engine('sqlite:///notfication.db', echo=True)
Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
metadata = MetaData(engine)
Base = declarative_base()

class Notfication(Base):
    __tablename__ = 'notfications'
    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(Text, nullable=False)
    status = Column(Integer, nullable=False)
    created_at = Column(DATETIME, default=datetime.now, nullable=False)
    updated_at = Column(DATETIME, default=datetime.now, nullable=False)

    def __init__(self, message):
        self.message = message
        self.status = 0
        now = datetime.now()
        self.created_at = now
        self.updated_at = now

Base.metadata.create_all(engine)

## api server
class NotficationsResource:

    def __init__(self, scheduler, store):
        self.scheduler = scheduler
        self.store = store

    def on_get(self, req, resp):
        notfication_id = self.store.add({})
        self.scheduler.add_job(notfication_job, '2017-03-15 18:06:00', args=[notfication_id])
        resp.body = str(notfication_id)

    def on_post(self, req, resp):
        pass

    def on_put(self, req, resp, notfication_id):
        pass

    def on_delete(self, req, resp, notfication_id):
        pass


## data store
class NotficationStore:

    def __init__(self, session):
        self.session = session

    def add(self, notfication):
        notfication = Notfication("test")
        self.session.add(notfication)
        self.session.commit()
        return notfication.id

    def remove(self, notfication_id):
        notfication = self.find(notfication_id)
        if notfication is not None:
            self.session.delete(notfication)
            self.session.commit

    def close(self):
        self.session.close

    def find(self, notfication_id):
        return self.session.query(Notfication).filter_by(id=notfication_id).first()


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

    def __init__(self, db_path='sqlite:///scheduler.db'):
        self.scheduler = Scheduler()
        self.scheduler.add_jobstore(SQLAlchemyJobStore(url=db_path), 'sqlite')
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


#    job = sched.add_interval_job(my_job, minutes=1, args=['hello'])
#    job = sched.add_date_job(job_function, '2013-08-05 23:47:05', ['hello'])

setproctitle('aws-sns-scheduler')
store = NotficationStore(Session())
scheduler = MyScheduler()

def notfication_job(notfication_id):
    notfication = store.find(notfication_id)
    print notfication.message

def receive_signal(signum, stack):
    store.close()
    scheduler.shutdown()

signal.signal(signal.SIGUSR1, receive_signal)
signal.signal(signal.SIGUSR2, receive_signal)

scheduler.start()
api = falcon.API()
api.add_route('/notfications', NotficationsResource(scheduler, store))
api.add_route('/notfications/{notfication_id}', NotficationsResource(scheduler, store))
