import models
import publisher


def notfication_task(notfication_id):
    store = models.create_store()
    notfication = store.find(notfication_id)
    if notfication is None or notfication.delivered():
        store.close()
        return
    try:
        print 'start notfication task:' + str(notfication_id)
        publisher.publish(notfication.message)
        store.update(notfication_id, {'delivery_status': 1})
        print 'end notfication task:' + str(notfication_id)
    except Exception as e:
        store.update(notfication_id, {'delivery_status': 2})
        print '=== error ==='
        print 'type:' + str(type(e))
        print 'args:' + str(e.args)
        print 'message:' + e.message
    finally:
        store.close()
