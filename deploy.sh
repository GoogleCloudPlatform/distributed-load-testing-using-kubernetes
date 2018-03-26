#!/bin/bash -xe

PROJECT_ID=$1

if [[ -z "${PROJECT_ID}" ]]; then
	exit 1
fi

sed -i "s/\$targetHost/http:\/\/${PROJECT_ID}.appspot.com/g;s/\$projectId/${PROJECT_ID}/g" kubernetes-config/locust-master-deployment.yaml
sed -i "s/\$targetHost/http:\/\/${PROJECT_ID}.appspot.com/g;s/\$projectId/${PROJECT_ID}/g" kubernetes-config/locust-worker-deployment.yaml

kubectl apply -f kubernetes-config