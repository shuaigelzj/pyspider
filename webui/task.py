#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2014-07-16 15:30:57

from app import app
from flask import abort, render_template, request, json

from libs import utils

@app.route('/task/<taskid>')
def task(taskid):
    if ':' not in taskid:
        abort(400)
    project, taskid = taskid.split(':', 1)

    taskdb = app.config['taskdb']
    task = taskdb.get_task(project, taskid)

    return render_template("task.html", task=task, json=json,
            status_to_string=app.config['taskdb'].status_to_string)

@app.route('/tasks')
def tasks():
    rpc = app.config['scheduler_rpc']
    taskdb = app.config['taskdb']
    limit = int(request.args.get('limit', 100))

    tasks = {}
    for updatetime, task in sorted(rpc.get_active_tasks(limit), key=lambda x: x[0]):
        task['updatetime'] = updatetime
        tasks['%(project)s:%(taskid)s' % task] = task

    return render_template("tasks.html", tasks=tasks.values(), status_to_string=taskdb.status_to_string)

@app.route('/active_tasks')
def active_tasks():
    rpc = app.config['scheduler_rpc']
    taskdb = app.config['taskdb']

    limit = int(request.args.get('limit', 100))
    tasks = rpc.get_active_tasks(limit)
    result = []
    for updatetime, task in tasks:
        task['updatetime'] = updatetime
        task['updatetime_text'] = utils.format_date(updatetime)
        if 'status' in task:
            task['status_text'] = taskdb.status_to_string(task['status'])
        result.append(task)

    return json.dumps(result), 200, {'Content-Type': 'application/json'}

app.template_filter('format_date')(utils.format_date)
