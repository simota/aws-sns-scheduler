import os
import sys
import time
import falcon
import json
import uuid
import signal
import threading
from wsgiref.simple_server import make_server
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
    scheduled_at = Column(DATETIME, nullable=False)
    created_at = Column(DATETIME, default=datetime.now, nullable=False)
    updated_at = Column(DATETIME, default=datetime.now, nullable=False)

    def __init__(self, message, schedule):
        self.message = message
        self.status = 0
        now = datetime.now()
        self.scheduled_at = schedule
        self.created_at = now
        self.updated_at = now

    def mark_completed(self):
        self.status = 1

    def mark_error(self):
        self.status = 2

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'message': self.message,
            'scheduled_at': self.scheduled_at.strftime('%Y-%m-%d %H:%M:%S')
            }

Base.metadata.create_all(engine)

## api server
class NotficationsResource:

    def __init__(self, scheduler, store):
        self.scheduler = scheduler
        self.store = store

    def on_get(self, req, resp):
        notfications = self.store.all()
        data = map(lambda x: x.to_dict(), notfications)
        resp.body = json.dumps({'notfication': data})

    def on_post(self, req, resp):
        message = req.params['message']
        schedule = datetime.strptime(req.params['schedule'], '%Y-%m-%d %H:%M:%S')
        notfication = self.store.add(message, schedule)
        self.scheduler.add_job(scheduler_task, schedule, args=[notfication.id])
        resp.body = json.dumps(notfication.to_dict())

    def on_put(self, req, resp, notfication_id):
        pass

    def on_delete(self, req, resp, notfication_id):
        pass


## data store
class NotficationStore:

    def __init__(self, session):
        self.session = session

    def add(self, message, schedule):
        notfication = Notfication(message, schedule)
        self.session.add(notfication)
        self.session.commit()
        return notfication

    def remove(self, notfication_id):
        notfication = self.find(notfication_id)
        if notfication is not None:
            self.session.delete(notfication)
            self.session.commit

    def update(self, notfication):
        self.session.add(notfication)
        self.session.commit

    def close(self):
        self.session.close

    def find(self, notfication_id):
        return self.session.query(Notfication).filter_by(id=notfication_id).first()

    def all(self):
        return self.session.query(Notfication).all()


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
        self.scheduler.add_jobstore(SQLAlchemyJobStore(url=db_path), 'default')
        self.scheduler.add_listener(self.event_listener, events.EVENT_ALL)

    def start(self):
        self.scheduler.start()


    def add_job(self, job, date, args):
        job = self.scheduler.add_date_job(job, date, args)
        print job

    def jobs(self):
        return self.scheduler.get_jobs

    def remove_job(self):
        pass

    def shutdown(self):
        self.scheduler.shutdown()

    def event_listener(self, event):
        print self.EVENTS[str(event.code)]
        self.scheduler.print_jobs()


setproctitle('aws-sns-scheduler')
store = NotficationStore(Session())
scheduler = MyScheduler()

def scheduler_task(notfication_id):
    try:
        print "notfication_job"
        s = NotficationStore(Session())
        notfication = s.find(notfication_id)
        print notfication.message
        notfication.mark_completed()
        s.update(notfication)
        s.close()
    except Exception as e:
        print '=== error ==='
        print 'type:' + str(type(e))
        print 'args:' + str(e.args)
        print 'message:' + e.message

def receive_signal(signum, stack):
    store.close()
    scheduler.shutdown()
    httpd.server_close()

signal.signal(signal.SIGUSR1, receive_signal)
signal.signal(signal.SIGUSR2, receive_signal)

scheduler.start()
api = falcon.API()
api.req_options.auto_parse_form_urlencoded = True
api.add_route('/notfications', NotficationsResource(scheduler, store))
api.add_route('/notfications/{notfication_id}', NotficationsResource(scheduler, store))

httpd = make_server('', 9999, api)
httpd.serve_forever()
