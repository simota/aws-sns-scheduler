import models
import publisher

def notfication_task(notfication_id):
    try:
        print 'start notfication task:' + str(notfication_id)
        s = models.create_store()
        notfication = s.find(notfication_id)
#        publisher.publish(notfication.message)
        s.update(notfication_id, {'delivery_status': 1})
        s.close()
        print 'end notfication task:' + str(notfication_id)
    except Exception as e:
        print '=== error ==='
        print 'type:' + str(type(e))
        print 'args:' + str(e.args)
        print 'message:' + e.message
