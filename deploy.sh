#!/bin/bash -xe

IMAGE_NAME=$1
TARGET_HOST=$2

if [[ -z "${IMAGE_NAME}" && -z "${TARGET_HOST}" ]]; then
	exit 1
fi

sed -i s/\$targetHost/${TARGET_HOST}/g kubernetes-config/environment-variable.yaml
sed -i s/\$imageName/${IMAGE_NAME}/g kubernetes-config/locust-master-deployment.yaml
sed -i s/\$imageName/${IMAGE_NAME}/g kubernetes-config/locust-worker-deployment.yaml

kubectl apply -f kubernetes-config --dry-run
kubectl create configmap locust-tasks-configuration --from-file=config/tasks.py
kubectl apply -f kubernetes-config