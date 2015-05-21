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


import webapp2
from google.appengine.ext import ndb


class StationMetric(ndb.Model):
    """
    Thermometer for measuring air and sea surface temperature
    Barometer for measuring atmospheric pressure
    Hygrometer for measuring humidity.
    Anemometer for measuring wind speed
    Rain gauge for measuring liquid precipitation over a set period of time.
    Present Weather/Precipitation Identification Sensor for identifying falling precipitation
    Disdrometer for measuring drop size distribution
    Transmissometer for measuring visibility
    Ceilometer for measuring cloud ceiling
    """
    stationid = ndb.StringProperty()
    recorded = ndb.DateTimeProperty(auto_now_add=True)
    temperature = ndb.FloatProperty()
    pressure = ndb.FloatProperty()
    humidity = ndb.FloatProperty()
    windspeed = ndb.FloatProperty()
    precipitation = ndb.FloatProperty()
    dropsize = ndb.FloatProperty()
    visibility = ndb.FloatProperty()
    ceiling = ndb.FloatProperty()


class HomeHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Workload Simulation Using Containers as Clients\n')


class LoginHandler(webapp2.RequestHandler):
    def post(self):
        stationid = self.request.get('stationid')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('/login - station: {}\n'.format(stationid))


class MetricsHandler(webapp2.RequestHandler):
    def post(self):
        stationid = self.request.get('stationid')

        sm = StationMetric(
            stationid = stationid,
            temperature = float(self.request.get('temperature')),
            pressure = float(self.request.get('pressure')),
            humidity = float(self.request.get('humidity')),
            windspeed = float(self.request.get('windspeed')),
            precipitation = float(self.request.get('precipitation')),
            dropsize = float(self.request.get('dropsize')),
            visibility = float(self.request.get('visibility')),
            ceiling = float(self.request.get('ceiling'))
        )
        smkey = sm.put()
        
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('/metrics - station: {}, kind: {}, id: {}\n'.
            format(stationid, smkey.kind(), smkey.id()))


app = webapp2.WSGIApplication([
    (r'/', HomeHandler),
    (r'/login', LoginHandler),
    (r'/metrics', MetricsHandler),
])
