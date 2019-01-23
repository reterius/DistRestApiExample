from __future__ import absolute_import
from celery import Celery

app = Celery('DistRestApiExample',
             broker='amqp://guest:guest@localhost:5672',
             backend='amqp://guest:guest@localhost:5672',
             include=['DistRestApiExample.CheckLoginWorker'])
