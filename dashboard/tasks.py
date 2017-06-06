from __future__ import absolute_import
from celery import shared_task
from celery.task import periodic_task
from datetime import timedelta
import redis

from dashboard.models import UserFile


@shared_task
def tasktest():
    pass


@periodic_task(run_every=timedelta(seconds=5))
def testing():
    date_test = UserFile.objects.get(pk=1)
    state = date_test.waarnings

    if not state:
        print("FALSE")
        date_test.waarnings = True
        date_test.save()
    else:
        print("TRUE")
        date_test.waarnings = False
        date_test.save()
