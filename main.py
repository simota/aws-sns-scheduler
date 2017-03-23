import signal
from setproctitle import setproctitle

import scheduler
import server
import models

def receive_signal(signum, stack):
    store.close()
    my_scheduler.close()
    server.close()


def setup_process():
    setproctitle('aws-sns-scheduler')
    signal.signal(signal.SIGUSR1, receive_signal)
    signal.signal(signal.SIGUSR2, receive_signal)


if __name__ == '__main__':
    setup_process()
    store = models.create_store()
    my_scheduler = scheduler.create_scheduler()
    my_scheduler.start()
    server.run(my_scheduler, store)
