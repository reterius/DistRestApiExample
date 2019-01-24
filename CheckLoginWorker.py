import sys
import os
from pymongo import MongoClient
import hashlib
import json
from bson import json_util
import pprint

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.TaskManagementDb

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path)
sys.path.insert(0, path)

from CeleryApp.CeleryObj import app


@app.task(name='DistRestApiExample.CheckLoginWorker.UserCheck')
def UserCheck(username, password):
    print(username + ' adli kisi icin UserCheck islemleri basladi')
    # time.sleep(20)
    UsersCollection = db.Users
    CryptedPassword = hashlib.md5(password.encode('utf-8')).hexdigest()
    UserRow = UsersCollection.find_one({"Username": username, "Password": CryptedPassword})

    User = json.loads(json_util.dumps(UserRow))
    pprint.pprint(User)

    response = {
        'IsLegalUser': True
    }
    if len(User) == 0:
        return response
    else:
        response['User'] = User
    print(username + ' adli kisi icin UserCheck islemleri bitti')
    return response
