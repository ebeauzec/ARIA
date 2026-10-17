# Quick start for Trident
Source: https://docs.netapp.com/us-en/trident/trident-get-started/quickstart.html
Fetched: 2026-07-07

You can install Trident and start managing storage resources in a few steps. Before getting started, review [Trident requirements](https://docs.netapp.com/us-en/trident/trident-get-started/requirements.html).

> Note: For Docker, refer to [Trident for Docker](https://docs.netapp.com/us-en/trident/trident-docker/deploy-docker.html).

## Step 1: Prepare the worker node

All worker nodes in the Kubernetes cluster must be able to mount the volumes you have provisioned for your pods. See [Prepare the worker node](https://docs.netapp.com/us-en/trident/trident-use/worker-node-prep.html).

## Step 2: Install Trident

Trident offers several installation methods and modes optimized for a variety of environments and organizations. See [Install Trident](https://docs.netapp.com/us-en/trident/trident-install/kubernetes-deploy.html).

## Step 3: Create a backend

A backend defines the relationship between Trident and a storage system. It tells Trident how to communicate with that storage system and how Trident should provision volumes from it. See [Configure a backend](https://docs.netapp.com/us-en/trident/trident-use/backends.html) for your storage system.

## Step 4: Create a Kubernetes StorageClass

The Kubernetes StorageClass object specifies Trident as the provisioner and allows you to create a storage class to provision volumes with customizable attributes. Trident creates a matching storage class for Kubernetes objects that specify the Trident provisioner. See [Create a storage class](https://docs.netapp.com/us-en/trident/trident-use/create-stor-class.html).

## Step 5: Provision a volume

A *PersistentVolume* (PV) is a physical storage resource provisioned by the cluster administrator on a Kubernetes cluster. The *PersistentVolumeClaim* (PVC) is a request for access to the PersistentVolume on the cluster.

Create a PersistentVolume (PV) and a PersistentVolumeClaim (PVC) that uses the configured Kubernetes StorageClass to request access to the PV. You can then mount the PV to a pod. See [Provision a volume](https://docs.netapp.com/us-en/trident/trident-use/vol-provision.html).

## What's next?

You can now add additional backends, manage storage classes, manage backends, and perform volume operations.
