# Workload Simulation Using Containers as Clients

## About

[Background](http://cloud.google.com/solutions/workload-simulation-using-containers-as-clients).

## Prerequisites

* Google Cloud Platform account
* Install and setup [Google Cloud SDK](https://cloud.google.com/sdk/)

**Note:** when installing the Google Cloud SDK you will need to enable the following additional components:

* App Engine SDK for Python and PHP
* Compute Engine Command Line Interface
* Developer Preview gcloud Commands
* gcloud Alpha Commands
* gcloud app Python Extensions
* kubectl

## Deploy Web Application

The `sample-webapp` folder contains a simple Google App Engine Python application as the "system under test". To deploy the application to your project, first edit the `application` field in `workload-simulation/sample-webapp/app.yaml` with your desired application name. Then use the `appcfg.py` tool to upload the app.

    $ cd workload-simulation/sample-webapp
    $ appcfg.py --oauth2 update .

## Build Docker Image

The Docker image has been pre-built and uploaded to the [Google Container Registry](http://gcr.io) however if you are interested in making changes and publishing a new image, refer to the following steps.

First, [install Docker](https://docs.docker.com/installation/#installation) on your platform. Once Docker is installed and you've made changes to the `Dockerfile`, you can build, tag, and upload the image using the following steps:

    $ docker build -t your-username/locust-tasks .
    $ docker tag your-username/locust-tasks gcr.io/your-project-id/locust-tasks
    $ gcloud preview docker --project your-project-id push gcr.io/your-project-id/locust-tasks

**Note:** you are not required to use the Google Container Registry. If you'd like to publish your images to the [Docker Hub](https://hub.docker.com) please refer to the steps to [Working with Docker Hub](https://docs.docker.com/userguide/dockerrepos/).

## Deploy Controllers and Services

The `locust-master` and `locust-worker` controllers are set to use the pre-built `locust-tasks` Docker image, available at [gcr.io/cloud-solutions-images/locust-tasks](http://gcr.io/cloud-solutions-images/locust-tasks). However, if you elected to rebuild the Docker image you will need to edit the controllers with your image location. Specifically, the `spec.template.spec.containers.image` field in each controller controls which Docker image to use.

If you uploaded your Docker image to the Google Container Registry:

    image: gcr.io/your-project-id/locust-tasks:latest

If you uploaded your Docker image to the Docker Hub:

    image: your-username/locust-tasks:latest

**Note:** the image location includes the `latest` tag so that the image is pulled down every time a new Pod is launched. To use a Kubernetes-cached copy of the image, remove `:latest` from the image location.

### Deploy Kubernetes Cluster

First create the [Google Container Engine](http://cloud.google.com/container-engine) cluster:

    $ gcloud alpha container clusters create your-cluster-name

After a few minutes, you'll have a working Kubernetes cluster with three nodes (not counting the Kubernetes master). Next, configure your system to use the `kubectl` command:

    $ export KUBECONFIG=/Users/your-username/.config/gcloud/kubernetes/kubeconfig
    $ kubectl config use-context gke_your-project-id_us-central1-b_your-cluster-name

**Note:** the output from the previous `gcloud` command will contain the specific commands you'll need to execute for your platform/project.

### Deploy locust-master

Now that `kubectl` is setup, deploy the `locust-master-controller`:

    $ kubectl create -f locust-master-controller.yaml

To confirm that the Replication Controller and Pod are created, run the following:

    $ kubectl get rc
    $ kubectl get pods -l name=locust,role=master

Next, deploy the `locust-master-service`:

    $ kubectl create -f locust-master-service.yaml

This step will expose the Pod with an internal DNS name (`locust-master`) and ports `8089`, `5557`, and `5558`. As part of this step, the `createExternalLoadBalancer` directive in `locust-master-service.yaml` will tell Google Container Engine to create a Google Compute Engine forwarding-rule from a publicly avaialble IP address to the `locust-master` Pod. To view the newly created forwarding-rule, execute the following:

    $ gcloud compute forwarding-rules list 

### Deploy locust-worker

Now deploy `locust-worker-controller`:

    $ kubectl create -f locust-worker-controller.yaml

The `locust-worker-controller` is set to deploy 10 `locust-worker` Pods, to confirm they were deployed run the following:

    $ kubectl get pods -l name=locust,role=worker

Next, deploy the `locust-worker-service`:

    $ kubectl create -f locust-worker-service.yaml 

This step will expose the Pods with an internal DNS name (`locust-worker`) and ports `5557` and `5558`, (additionally as part of the Service layer, an internal proxy is created to load balance across the worker instances using the internal DNS name).

### Setup Firewall Rules

The final step in deploying these controllers and services is to allow traffic from your publicly accessible forwarding-rule IP address to the appropriate Container Engine instances.

The only traffic we need to allow externally is to the Locust web interface, running on the `locust-master` Pod at port `8089`. To create the firewall rule, execute the following:

    $ gcloud compute firewall-rules create firewall-rule-name --allow=tcp:8089 --target-tags k8s-cluster-name-node

## Execute Tests

To execute the Locust tests, navigate to the IP address of your forwarding-rule and port `8089` and enter the number of clients to spawn and the client hatch rate.

## License

This code is Apache 2.0 licensed and more information can be found in `LICENSE`.