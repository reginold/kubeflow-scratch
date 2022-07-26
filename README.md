# Introduction
- [kubeflow-scratch](#kubeflow-scratch)
  - [Create the basic kubeflow based on AWS EKS.](#create-the-basic-kubeflow-based-on-aws-eks)
    - [Create an EKS cluster and install Kubeflow](#create-an-eks-cluster-and-install-kubeflow)
    - [Access Kubeflow central dashboard](#access-kubeflow-central-dashboard)
    - [Create a container registry](#create-a-container-registry)
    - [Create the S3 bucket](#create-the-s3-bucket)
    - [Create the Kubeflow pipeline](#create-the-kubeflow-pipeline)
# kubeflow-scratch
## Create the basic kubeflow based on AWS EKS.

In this guide, we will go through every step that is necessary to have a functioning pipeline. You will learn how to :

- Create a Kuberneter cluster
- Install Kubeflow
- Create a container registry
- Build a container image and push it to your registry
- Give Kubeflow access to your S3 buckets
- Create Kubeflow components with input and output artifacts
- Create a Kubeflow pipeline, upload it and run it


### Create an EKS cluster and install Kubeflow
- Be sure not to miss the following prerequisites
  - AWS CLI - A command line tool for interacting with AWS services.
  - eksctl - A command line tool for working with EKS clusters.
  kubectl - A command line tool for working with Kubernetes clusters.
  - yq - A command line tool for YAML processing. (For Linux environments, use the wget plain binary installation)
  - jq - A command line tool for processing JSON.
  - kustomize version 3.2.0 - A command line tool to customize Kubernetes objects through a kustomization file.
  - Configure - AWS CLI by running the following command: aws configure.
    - Enter your Access Keys (Access Key ID and Secret Access Key).
    - Enter your preferred AWS Region and default output options.
  - Install aws-iam-authenticator.
- Create the kubeflow cluster on AWS(EKS)
  - Set the config
    ```
    export CLUSTER_NAME=kubeflow-demo
    export CLUSTER_REGION=ap-northeast-1
    export K8S_VERSION=1.21(info: check the latest version)
    export EC2_INSTANCE_TYPE=p2.xlarge
    ```
  - Create the cluster
    ```
    eksctl create cluster \
    --name ${CLUSTER_NAME} \
    --version  ${K8S_VERSION} \
    --region ${CLUSTER_REGION} \
    --nodegroup-name linux-nodes \
    --node-type  ${EC2_INSTANCE_TYPE} \
    --nodes 1 \
    --nodes-min 1 \
    --nodes-max 2 \
    --managed \
    --with-oidc
    ``` 
### Access Kubeflow central dashboard
  - ```kubectl get ingress -n istio-system```
    - return an address like
      - ```123-istiosystem-istio-2af2-4567.ap-northeast-1.elb.amazonaws.com```

### Create a container registry
- Install docker on aws
- get-login-password (AWS CLI)
  - `aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${aws_account_id}.dkr.ecr.${region}.amazonaws.com`
- Create a repository
  - `aws ecr create-repository \
    --repository-name kubeflow-demo \
    --image-scanning-configuration scanOnPush=true \
    --region region`
- Create a container
  - `docker build -t kubeflow-image .`
- Tage the image
  - `docker push ${aws_account_id}.dkr.ecr.${region}.amazonaws.com/kubeflow-demo:latest`
### Create the S3 bucket
- Test if you have access to S3
```.py
import boto3

conn = boto3.client('s3')
contents = conn.list_objects(Bucket=bucket_name)['Contents']
for f in contents:
    print(f['Key'])
```
### Create the Kubeflow pipeline
- Refer to the `kubeflow_pipiline.py`

