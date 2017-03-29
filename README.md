## Distributed Load Testing Using Kubernetes

This tutorial demonstrates how to conduct distributed load testing using [Kubernetes](http://kubernetes.io) and includes a sample web application, Docker image, and Kubernetes controllers/services. For more background refer to the [Distributed Load Testing Using Kubernetes](http://cloud.google.com/solutions/distributed-load-testing-using-kubernetes) solution paper.

## Prerequisites

* Google Cloud Platform account
* Install and setup [Google Cloud SDK](https://cloud.google.com/sdk/)

**Note:** when installing the Google Cloud SDK you will need to enable the following additional components:

* `App Engine Command Line Interface (Preview)`
* `App Engine SDK for Python and PHP`
* `Compute Engine Command Line Interface`
* `Developer Preview gcloud Commands`
* `gcloud Alpha Commands`
* `gcloud app Python Extensions`
* `kubectl`


** Update March 2017
After installing the google cloud SDK, run the following

    $ gcloud init

Chose to login, a web page will open. Chose allow in the permissions dialog, when complete a success message will display.

Swap back to the console window.
Select "Y" to indicate that you wish to configure compute engine.
You will be given choices for projects and zones

Before continuing, you can also set your preferred zone and project:

    $ gcloud config set compute/zone ZONE
    $ gcloud config set core/project PROJECT-ID


** Update March 2017
After setting the preferred zone and project, you can verify the configuration:

    $ gcloud config list

## Install kubectl

    $ gcloud components install kubectl
    $ gcloud container clusters get-credentials PROJECT-ID
    $ gcloud auth application-default login

## Deploy Web Application

The `sample-webapp` folder contains a simple Google App Engine Python application as the "system under test". To deploy the application to your project use the `gcloud preview app deploy` command.

    $ gcloud app deploy sample-webapp/app.yaml --project=PROJECT-ID --set-default

**Note:** you will need the URL of the deployed sample web application when deploying the `locust-master` and `locust-worker` controllers.

## Deploy Controllers and Services

Before deploying the `locust-master` and `locust-worker` controllers, update each to point to the location of your deployed sample web application. Set the `TARGET_HOST` environment variable found in the `spec.template.spec.containers.env` field to your sample web application URL.

    - name: TARGET_HOST
      key: TARGET_HOST
      value: http://PROJECT-ID.appspot.com

### Update Controller Docker Image (Optional)

The `locust-master` and `locust-worker` controllers are set to use the pre-built `locust-tasks` Docker image, which has been uploaded to the [Google Container Registry](http://gcr.io) and is available at `gcr.io/cloud-solutions-images/locust-tasks`. If you are interested in making changes and publishing a new Docker image, refer to the following steps.

First, [install Docker](https://docs.docker.com/installation/#installation) on your platform. Once Docker is installed and you've made changes to the `Dockerfile`, you can build, tag, and upload the image using the following steps:

    $ docker build -t USERNAME/locust-tasks .
    $ docker tag USERNAME/locust-tasks gcr.io/PROJECT-ID/locust-tasks
    $ gcloud preview docker --project PROJECT-ID push gcr.io/PROJECT-ID/locust-tasks

**Note:** you are not required to use the Google Container Registry. If you'd like to publish your images to the [Docker Hub](https://hub.docker.com) please refer to the steps in [Working with Docker Hub](https://docs.docker.com/userguide/dockerrepos/).

Once the Docker image has been rebuilt and uploaded to the registry you will need to edit the controllers with your new image location. Specifically, the `spec.template.spec.containers.image` field in each controller controls which Docker image to use.

If you uploaded your Docker image to the Google Container Registry:

    image: gcr.io/PROJECT-ID/locust-tasks:latest

If you uploaded your Docker image to the Docker Hub:

    image: USERNAME/locust-tasks:latest

**Note:** the image location includes the `latest` tag so that the image is pulled down every time a new Pod is launched. To use a Kubernetes-cached copy of the image, remove `:latest` from the image location.

### Deploy Kubernetes Cluster

First create the [Google Container Engine](http://cloud.google.com/container-engine) cluster using the `gcloud` command as shown below. 

**Note:** This command defaults to creating a three node Kubernetes cluster (not counting the master) using the `n1-standard-1` machine type. Refer to the [`gcloud alpha container clusters create`](https://cloud.google.com/sdk/gcloud/reference/alpha/container/clusters/create) documentation information on specifying a different cluster configuration.

    $ gcloud container clusters create CLUSTER-NAME

After a few minutes, you'll have a working Kubernetes cluster with three nodes (not counting the Kubernetes master). To see the cluster deatails issue the following:

    $ gcloud container clusters list

Try running:

    $ kubectl cluster-info

If cluster information is displayed, the following may not be necessary...


Next, configure your system to use the `kubectl` command:

    $ kubectl config use-context gke_PROJECT-ID_ZONE_CLUSTER-NAME

**Note:** the output from the previous `gcloud` cluster create command will contain the specific `kubectl config` command to execute for your platform/project.


For more information on kubectl commands check out kubectl cheat sheet:  [Kubernetes Cheat Sheet](https://kubernetes.io/docs/user-guide/kubectl-cheatsheet/)


### Deploy locust-master

Now that `kubectl` is setup, deploy the `locust-master-controller`, cd to the kubernetes-config directory, and run :

    $ kubectl create -f locust-master-controller.yaml

To confirm that the Replication Controller and Pod are created, run the following:

    $ kubectl get rc
    $ kubectl get pods -l name=locust,role=master

Next, deploy the `locust-master-service`:

    $ kubectl create -f locust-master-service.yaml

This step will expose the Pod with an internal DNS name (`locust-master`) and ports `8089`, `5557`, and `5558`. As part of this step, the `type: LoadBalancer` directive in `locust-master-service.yaml` will tell Google Container Engine to create a Google Compute Engine forwarding-rule from a publicly avaialble IP address to the `locust-master` Pod. To view the newly created forwarding-rule, execute the following:

    $ gcloud compute forwarding-rules list

    $ kubectl get svc

### Deploy locust-worker

Now deploy `locust-worker-controller`:

    $ kubectl create -f locust-worker-controller.yaml

The `locust-worker-controller` is set to deploy 10 `locust-worker` Pods, to confirm they were deployed run the following:

    $ kubectl get pods -l name=locust,role=worker

To scale the number of `locust-worker` Pods, issue a replication controller `scale` command.

    $ kubectl scale --replicas=20 replicationcontrollers locust-worker

To confirm that the Pods have launched and are ready, get the list of `locust-worker` Pods:

    $ kubectl get pods -l name=locust,role=worker

**Note:** depending on the desired number of `locust-worker` Pods, the Kubernetes cluster may need to be launched with more than 3 compute engine nodes and may also need a machine type more powerful than n1-standard-1. Refer to the [`gcloud alpha container clusters create`](https://cloud.google.com/sdk/gcloud/reference/alpha/container/clusters/create) documentation for more information.

### Setup Firewall Rules

The final step in deploying these controllers and services is to allow traffic from your publicly accessible forwarding-rule IP address to the appropriate Container Engine instances.

The only traffic we need to allow externally is to the Locust web interface, running on the `locust-master` Pod at port `8089`. First, get the target tags for the nodes in your Kubernetes cluster using the output from `kubectl get nodes`:

    $ kubectl get nodes
    NAME                        LABELS                                             STATUS
    gke-ws-0e365264-node-4pdw   kubernetes.io/hostname=gke-ws-0e365264-node-4pdw   Ready
    gke-ws-0e365264-node-jdcz   kubernetes.io/hostname=gke-ws-0e365264-node-jdcz   Ready
    gke-ws-0e365264-node-kp3d   kubernetes.io/hostname=gke-ws-0e365264-node-kp3d   Ready

The target tag is the node name prefix up to `-node` and is formatted as `gke-CLUSTER-NAME-[...]-node`. For example, if your node name is `gke-mycluster-12345678-node-abcd`, the target tag would be `gke-mycluster-12345678-node`. 

Now to create the firewall rule, execute the following:

    $ gcloud compute firewall-rules create FIREWALL-RULE-NAME --allow=tcp:8089 --target-tags gke-CLUSTER-NAME-[...]-node


Verify there is a rule with tcp:8089 pointing to the correct target_tag by running:

    $ gcloud compute firewall-rules list


## Execute Tests

To execute the Locust tests, navigate to the IP address of your forwarding-rule (see above) and port `8089`, run:

    $ kubectl get svc

Use the IP_ADDRESS to access the console on port 8089

enter the number of clients to spawn and the client hatch rate then start the simulation.


To watch the demo application / System Under Test run:

    $ gcloud app logs tail -s default

To check out the logs on the pods:

    $ kubectl get pods

chose a pod and use the name in the below:

    $ kubectl logs --tail=20 POD_NAME

## Deployment Cleanup

To teardown the workload simulation cluster, use the following steps. First, delete the Kubernetes cluster:

    $ gcloud container clusters list
    $ gcloud container clusters delete CLUSTER-NAME

Next, delete the forwarding rule that forwards traffic into the cluster.

    $ gcloud compute forwarding-rules list
    $ gcloud compute forwarding-rules delete FORWARDING-RULE-NAME

Finally, delete the firewall rule that allows incoming traffic to the cluster.

    $ gcloud compute firewall-rules list
    $ gcloud compute firewall-rules delete FIREWALL-RULE-NAME

To delete the sample web application, visit the [Google Cloud Console](https://console.developers.google.com).

## License

This code is Apache 2.0 licensed and more information can be found in `LICENSE`. For information on licenses for third party software and libraries, refer to the `docker-image/licenses` directory.