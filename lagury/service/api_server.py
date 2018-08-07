from flask import Flask, request, make_response
app = Flask(__name__)


@app.route('/task_manager/api/v1/task', methods=['POST'])
def add_task():
    pass


@app.route('/task_manager/api/v1/task/local', methods=['POST'])
def add_task_local():
    data = request.json
