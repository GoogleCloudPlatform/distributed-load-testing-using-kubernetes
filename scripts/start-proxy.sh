# Copyright 2022 Google Inc. All rights reserved.
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

set -e

gcloud compute instances create-with-container ${PROXY_VM}    \
     --zone ${ZONE} \
     --container-image gcr.io/cloud-marketplace/google/nginx1:latest \
     --container-mount-host-path=host-path=/tmp/server.conf,mount-path=/etc/nginx/conf.d/default.conf \
     --metadata=startup-script="#! /bin/bash
       cat <<EOF > /tmp/server.conf
       server {
           listen 8089;
           location / {
               proxy_pass http://${INTERNAL_LB_IP}:8089;
           }
       }
EOF"

echo "To open an SSH tunnel between your workstation and this proxy instance, use this command:"
echo "  gcloud compute ssh --zone ${ZONE} ${PROXY_VM} -- -N -L 8089:localhost:8089"
