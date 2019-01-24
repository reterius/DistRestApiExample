from flask import Flask, jsonify, abort, request, url_for
from flask_jwt_extended import (
    JWTManager, create_access_token,
    create_refresh_token, jwt_required,
    jwt_refresh_token_required, get_jwt_identity
)

from CheckLoginWorker import UserCheck
import time
import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
from bson import json_util
import pprint

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.TaskManagementDb

app = Flask(__name__, static_url_path="")
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!

jwt = JWTManager(app)


@app.route('/todo/api/v1.0/CheckLoginApi', methods=['POST'])
def CheckLoginApi():
    username = request.json['username']
    password = request.json['password']

    startWorkerReq = int(round(time.time() * 1000))
    result = UserCheck.delay(username, password)

    while True:
        if result.ready() == True:
            finishWorkerReq = int(round(time.time() * 1000))
            ProcessTime = finishWorkerReq - startWorkerReq
            print("ProcessTime: " + str(ProcessTime))
            # at this time, our task is not finished, so it will return False
            print('Task finished? ', result.ready())
            print('Task result: ', result.result)
            if (result.result['IsLegalUser'] == False):
                abort(404)

            ret = {
                'access_token': create_access_token(identity=result.result['User']),
                'refresh_token': create_refresh_token(identity=result.result['User'])
            }
            return jsonify(ret), 200
            break


@app.route('/todo/api/v1.0/RefreshToken', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    UserDetails = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=UserDetails)
    }
    return jsonify(ret), 200


def make_public_task(task):
    new_task = {}
    for field in task:
        if field == '_id':
            new_task['_id'] = task['_id']['$oid']
            new_task['uri'] = url_for('get_task', task_id=task['_id']['$oid'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task


@app.route('/todo/api/v1.0/ListAllTasks', methods=['POST'])
@jwt_required
def get_tasks():
    TasksCollection = db.Tasks
    TasksList = []
    UserDetails = get_jwt_identity()
    for TaskRow in TasksCollection.find({
        "$and":
            [
                {
                    "UserID": ObjectId(UserDetails['_id']['$oid'])
                }
            ]
    }).sort([("_id", -1)]):
        TasksList.append(json.loads(json_util.dumps(TaskRow)))

    return jsonify({'tasks': list(map(make_public_task, TasksList))})


@app.route('/todo/api/v1.0/CreateTask', methods=['POST'])
@jwt_required
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)

    UserDetails = get_jwt_identity()

    pprint.pprint(UserDetails)
    pprint.pprint(UserDetails['_id']['$oid'])

    Task = {
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False,
        'date': datetime.datetime.utcnow(),
        'UserID': ObjectId(UserDetails['_id']['$oid'])
    }

    TasksCollection = db.Tasks
    TaskID = TasksCollection.insert_one(Task).inserted_id
    TaskRow = TasksCollection.find_one({"_id": ObjectId(TaskID)})
    Task = json.loads(json_util.dumps(TaskRow))

    return jsonify({'task': make_public_task(Task)}), 201


@app.route('/todo/api/v1.0/TaskDetail/<task_id>', methods=['GET'])
@jwt_required
def get_task(task_id):
    UserDetails = get_jwt_identity()
    TasksCollection = db.Tasks
    TaskRow = TasksCollection.find_one({"_id": ObjectId(task_id), 'UserID': ObjectId(UserDetails['_id']['$oid'])})
    Task = json.loads(json_util.dumps(TaskRow))

    if (Task is None):
        abort(404)
    return jsonify({'task': make_public_task(Task)})


@app.route('/todo/api/v1.0/UpdateTask', methods=['PUT'])
@jwt_required
def update_task():
    UserDetails = get_jwt_identity()

    TaskID = request.json['TaskID']
    TasksCollection = db.Tasks
    RowCount = TasksCollection.count_documents({'_id': ObjectId(TaskID)})

    if RowCount == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != str:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not str:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)

    TasksCollection.update_one({
        '_id': ObjectId(TaskID),
        'UserID': ObjectId(UserDetails['_id']['$oid'])
    }, {
        '$set': {
            'title': request.json['title'],
            'description': request.json['description'],
            'done': request.json['done']
        }
    }, upsert=False)

    TaskRow = TasksCollection.find_one({"_id": ObjectId(TaskID)})
    Task = json.loads(json_util.dumps(TaskRow))

    return jsonify({'task': make_public_task(Task)})


@app.route('/todo/api/v1.0/DeleteTask/<task_id>', methods=['DELETE'])
@jwt_required
def delete_task(task_id):
    UserDetails = get_jwt_identity()
    TasksCollection = db.Tasks

    RowCount = TasksCollection.count_documents({
        '_id': ObjectId(task_id),
        'UserID': ObjectId(UserDetails['_id']['$oid'])
    })
    if RowCount == 0:
        abort(404)
    TasksCollection.delete_one({
        '_id': ObjectId(task_id),
        'UserID': ObjectId(UserDetails['_id']['$oid'])
    })

    return jsonify({'result': True})


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
