from datetime import datetime, timedelta
import json
import falcon
from wsgiref.simple_server import make_server
import tasks
import publisher


class NotficationsResource:

    def __init__(self, scheduler, store):
        self.scheduler = scheduler
        self.store = store

    def on_get(self, req, resp):
        if 'delivery_status' in req.params:
            notfications = self.store.filter_by(
                {'delivery_status': req.params['delivery_status']})
        else:
            notfications = self.store.all()
        data = map(lambda x: x.to_dict(), notfications)
        resp.body = json.dumps({'notfications': data})

    def on_post(self, req, resp):
        error = self.validate_notfication(req.params)
        if error is not None:
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(error)
            return

        message = req.params['message']
        schedule = self.convert_datetime(req.params['schedule'])
        notfication = self.store.add(message, schedule)
        self.scheduler.add_job(tasks.notfication_task,
                               schedule, args=[notfication.id])

        resp.status = falcon.HTTP_201
        resp.body = json.dumps(notfication.to_dict())

    def on_put(self, req, resp, notfication_id):
        notfication = self.store.find(notfication_id)
        if notfication is None:
            resp.status = falcon.HTTP_404
            return

        error = self.validate_notfication(req.params)
        if error is not None:
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(error)
            return

        self.scheduler.remove_job(notfication_id)

        message = req.params['message']
        schedule = self.convert_datetime(req.params['schedule'])
        self.store.update(notfication_id, {
            'message': message,
            'scheduled_at': schedule})
        self.scheduler.add_job(tasks.notfication_task,
                               schedule, args=[notfication_id])

        notfication = self.store.find(notfication_id)
        resp.body = json.dumps(notfication.to_dict())

    def on_delete(self, req, resp, notfication_id):
        notfication = self.store.find(notfication_id)
        if notfication is None:
            resp.status = falcon.HTTP_404
            return

        self.scheduler.remove_job(notfication_id)
        self.store.remove(notfication_id)

        resp.status = falcon.HTTP_204
        resp.body = json.dumps({'notfication_id': notfication_id})

    def convert_datetime(self, date_string):
        if date_string == 'now':
            today = datetime.today()
            return today + timedelta(seconds=30)
        return datetime.strptime(
            date_string, '%Y-%m-%d %H:%M:%S')

    def validate_notfication(self, params):
        if 'message' not in params:
            return {'error_message': 'message is required'}
        if 'message' in params and len(params['message']) > 70:
            return {'error_message': 'message is too long'}
        if 'schedule' not in params:
            return {'error_message': 'schedule is required'}
        if params['schedule'] == 'now':
            return None

        schedule = None
        try:
            schedule = datetime.strptime(
                params['schedule'], '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            return {'error_message': 'schedule is invalid format'}

        if self.convert_datetime('now') > schedule:
            return {'error_message': 'schedule is over'}

        return None


class TargetsResource:

    def on_get(self, req, resp):
        resp.body = json.dumps(publisher.publish_targets())


def run(scheduler, store):
    api = falcon.API()
    api.req_options.auto_parse_form_urlencoded = True
    api.add_route('/notfications', NotficationsResource(scheduler, store))
    api.add_route('/notfications/{notfication_id}',
                  NotficationsResource(scheduler, store))
    api.add_route('/targets', TargetsResource())
    httpd = make_server('0.0.0.0', 8080, api)
    httpd.serve_forever()
