from celery import shared_task
import time


@shared_task
def notify_shit(message):
    print("helloo")
    time.sleep(10)
    print('finished man')