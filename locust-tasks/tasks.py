#!/usr/bin/env python

# Copyright 2015 Google Inc. All rights reserved.
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


import random
import uuid

from datetime import datetime
from locust import HttpLocust, TaskSet, task


class MetricsTaskSet(TaskSet):
    _stationid = None

    def on_start(self):
        self._stationid = str(uuid.uuid4())

    @task(1)
    def login(self):
        self.client.post('/login', {"stationid": self._stationid})

    @task(99)
    def post_metrics(self):
        self.client.post(
            "/metrics",
            {
                "stationid": self._stationid,
                "timestamp": datetime.now(),
                "temperature": random.uniform(0,100),
                "pressure": random.uniform(0,100),
                "humidity": random.uniform(0,100),
                "windspeed": random.uniform(0,100),
                "precipitation": random.uniform(0,100),
                "dropsize": random.uniform(0,100),
                "visibility": random.uniform(0,100),
                "ceiling": random.uniform(0,100)
            }
        )


class MetricsLocust(HttpLocust):
    task_set = MetricsTaskSet