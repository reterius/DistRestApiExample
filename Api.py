from flask import Flask, jsonify, abort, request, url_for
from flask_jwt_extended import (
    JWTManager, create_access_token,
    create_refresh_token, jwt_required,
    jwt_refresh_token_required, get_jwt_identity
)

from CheckLoginWorker import UserCheck

import time

app = Flask(__name__, static_url_path="")
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!

jwt = JWTManager(app)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


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
            if (result.result['IsLegalUser'] == True):
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
        if field == 'id':
            new_task['id'] = task['id']
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task


@app.route('/todo/api/v1.0/ListAllTasks', methods=['POST'])
@jwt_required
def get_tasks():
    return jsonify({'tasks': list(map(make_public_task, tasks))})


@app.route('/todo/api/v1.0/CreateTask', methods=['POST'])
@jwt_required
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': make_public_task(task)}), 201


@app.route('/todo/api/v1.0/TaskDetail/<int:task_id>', methods=['POST'])
@jwt_required
def get_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    return jsonify({'task': make_public_task(task[0])})


@app.route('/todo/api/v1.0/UpdateTask/<int:task_id>', methods=['PUT'])
@jwt_required
def update_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))

    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != str:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not str:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': make_public_task(task[0])})


@app.route('/todo/api/v1.0/DeleteTask/<int:task_id>', methods=['DELETE'])
@jwt_required
def delete_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
