import sys
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
        publisher.publish_to_topic(notfication.message)
        store.update(notfication_id, {'delivery_status': 1})
        print 'end notfication task:' + str(notfication_id)
    except:
        store.update(notfication_id, {'delivery_status': 2})
        print sys.exc_info()
    finally:
        store.close()
