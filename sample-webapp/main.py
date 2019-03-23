#!/usr/bin/env python

# Copyright 2019 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def root():
    return 'Welcome to the "Distributed Load Testing Using Kubernetes" sample web app\n'

@app.route('/login',  methods=['GET', 'POST'])
def login():
    deviceid = request.values.get('deviceid')
    return '/login - device: {}\n'.format(deviceid)

@app.route('/metrics',  methods=['GET', 'POST'])
def metrics():
    deviceid = request.values.get('deviceid')
    timestamp = request.values.get('timestamp')
    
    return '/metrics - device: {}, timestamp: {}\n'.format(deviceid, timestamp)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
