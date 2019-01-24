from pymongo import MongoClient
import pprint
import datetime
from bson.objectid import ObjectId
import hashlib

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.TaskManagementDb
TasksCollection = db.Tasks
UsersCollection = db.Users

#######################################################
# Inserting a Document
"""
Task = {
        'title': 'Task3 title',
        'description': 'task3 description',
        'done': False,
        'date': datetime.datetime.utcnow()
        }

TaskID = TasksCollection.insert_one(Task).inserted_id
print(TaskID)

"""

"""
CryptedPassword = hashlib.md5("456".encode('utf-8')).hexdigest()
User = {
    'Fullname': 'Ali Veli',
    'Username': 'aliveli',
    'Password': CryptedPassword,
    'Role': 'Super',
    'RegDate': datetime.datetime.utcnow()
}

UserID = UsersCollection.insert_one(User).inserted_id
"""
#######################################################
# Getting a Single Document With find_one()
"""
row = TasksCollection.find_one({"title": "Task2 title"})
pprint.pprint(row)
"""

"""
TaskID = "5c48368067011a95eae6b2ec"
row = TasksCollection.find_one({"_id": ObjectId(TaskID)})
pprint.pprint(row)
"""
########################################################
# Update Document
"""
TasksCollection.update_one({
  '_id': ObjectId("5c495ec467011a7c2131884d")
},{
  '$set': {
    'title': 'Selçuk task 3 title'
  }
}, upsert=False)

"""
########################################################
# Row Count
"""
RowCount = TasksCollection.count_documents({'_id': ObjectId("5c495ec467011a7c2131884d")})
"""
########################################################
# Get Multipple row
"""
for Task in TasksCollection.find({
    "$or":
        [
            {"$or":
                [
                    {
                        "UserID": ObjectId("5c48525a67011acdd517d41a"),
                        "done": True,
                        "title": {"$regex": "^baslik"}
                    },
                    {
                        "title": {"$regex": "task 2"},
                        "done": True
                    }
                ]
            },
            {
                "UserID": ObjectId("5c48525a67011acdd517d41a"),
                "done": False,
                "title": {"$regex": "task 1"}
            }
        ]
}).sort([("_id", 1)]).skip(0).limit(3):
    pprint.pprint(Task)
"""
