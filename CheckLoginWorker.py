import sys
import os

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path)
sys.path.insert(0, path)

from CeleryApp.CeleryObj import app

import time

Users = [
    {
        'id': 1,
        'Fullname': u'Selcuk Akkurt',
        'Username': u'reterius',
        'Password': u'123',
        'Role': u'Super',
    },
    {
        'id': 2,
        'Fullname': u'Ali Veli',
        'Username': u'aliveli',
        'Password': u'456',
        'Role': u'Normal',
    }
]


@app.task(name='DistRestApiExample.CheckLoginWorker.UserCheck')
def UserCheck(username, password):
    print(username + ' adli kisi icin UserCheck islemleri basladi')
    #time.sleep(20)
    User = list(filter(lambda u: u['Username'] == username and u['Password'] == password, Users))
    response = {
        'IsLegalUser': False
    }
    if len(User) == 0:
        return response
    else:
        response['User'] = User[0]
    print(username + ' adli kisi icin UserCheck islemleri bitti')
    return response
