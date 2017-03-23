from datetime import datetime
import json
import falcon
from wsgiref.simple_server import make_server
import tasks


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
        schedule = datetime.strptime(
            req.params['schedule'], '%Y-%m-%d %H:%M:%S')
        notfication = self.store.add(message, schedule)
        self.scheduler.add_job(tasks.notfication_task,
                               schedule, args=[notfication.id])
        resp.body = json.dumps(notfication.to_dict())

    def on_put(self, req, resp, notfication_id):
        pass

    def on_delete(self, req, resp, notfication_id):
        if self.scheduler.remove_job(notfication_id):
            self.store.remove(notfication_id)
        resp.body = json.dumps({})


def run(scheduler, store):
    api = falcon.API()
    api.req_options.auto_parse_form_urlencoded = True
    api.add_route('/notfications', NotficationsResource(scheduler, store))
    api.add_route('/notfications/{notfication_id}',
                  NotficationsResource(scheduler, store))
    httpd = make_server('', 9999, api)
    httpd.serve_forever()
