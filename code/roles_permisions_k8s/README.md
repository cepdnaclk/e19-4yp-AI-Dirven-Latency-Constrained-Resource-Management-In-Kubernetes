---
# Kubernetes CronJobs and Scripts Setup

This guide will explain how to apply the necessary **Kubernetes roles and permissions**, followed by the **CronJob** and **script** files required for CPU and memory limit reduction.
---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Roles and Permissions Setup](#roles-and-permissions-setup)
3. [Applying the CronJobs and Scripts](#applying-the-cronjobs-and-scripts)
4. [Job Types](#job-types)
5. [Verification](#verification)
6. [Cleanup](#cleanup)

---

## Prerequisites

Before applying the **CronJob** and **script** resources, ensure that your Kubernetes cluster is up and running.

You will need:

- Access to the Kubernetes cluster (`kubectl` configured properly).
- Permission to create resources like Roles, RoleBindings, CronJobs, and ConfigMaps.

---

## Roles and Permissions Setup

Before applying the **CronJobs** and **scripts**, we need to create the necessary **Roles** and **RoleBindings** to allow the CronJobs to interact with the Kubernetes API. These resources are stored in the `roles_permisions_k8s` folder:

### 1. Apply the Role

This Role defines the permissions required for CronJobs to access and modify resources (e.g., Deployments). It allows the required actions such as `get`, `list`, and `patch`.

```bash
kubectl apply -f role.yaml
```

### 2. Apply the RoleBinding

This RoleBinding binds the Role to the **default** service account, granting it the permissions defined in the Role. It ensures that the CronJobs can use the appropriate access rights.

```bash
kubectl apply -f rolebinding.yaml
```

---

## Applying the CronJobs and Scripts

After applying the **roles and permissions**, navigate to the relevant folder for each service and apply the CronJobs and script files.

### 1. Apply the CronJob and Script for CPU Limit Reduction

For **reduce-cpu-service**, go to the folder containing `reduce-cpu-service-cronjob.yaml` and `reduce-cpu-service-script.yaml`, and run the following commands:

```bash
kubectl apply -f reduce-cpu-service-cronjob.yaml
kubectl apply -f reduce-cpu-service-script.yaml
```

### 2. Apply the CronJob and Script for Memory Limit Reduction

For **reduce-mem-service**, go to the folder containing `reduce-mem-service-cronjob.yaml` and `reduce-mem-service-script.yaml`, and run the following commands:

```bash
kubectl apply -f reduce-mem-service-cronjob.yaml
kubectl apply -f reduce-mem-service-script.yaml
```

### 3. Apply the CronJob and Script for CPU and Memory Reduction

For **reduce-cpu-mem-service**, go to the folder containing `reduce-cpu-mem-service-cronjob.yaml` and `reduce-cpu-mem-service-script.yaml`, and run the following commands:

```bash
kubectl apply -f reduce-cpu-mem-service-cronjob.yaml
kubectl apply -f reduce-cpu-mem-service-script.yaml
```

---

## Job Types

The following **CronJobs** are defined for each service:

1. **reduce-cpu-service-cronjob**: This CronJob reduces the CPU limit of a deployment while keeping the memory limit constant.
2. **reduce-mem-service-cronjob**: This CronJob reduces the memory limit of a deployment while keeping the CPU limit constant.
3. **reduce-cpu-mem-service-cronjob**: This CronJob reduces both CPU and memory limits of a deployment.

---

## Verification

Once the CronJobs and scripts have been applied, you can verify their creation and check the CronJob's status by running:

```bash
kubectl get cronjobs
```

To see if the jobs are running correctly, you can monitor the logs of the created jobs:

```bash
kubectl logs job/<job-name>
```

For example, to check logs for a specific job, use:

```bash
kubectl logs job/reduce-cpu-service-job-<timestamp>
```

---

## Cleanup

To remove the CronJobs, scripts, roles, and rolebindings, follow these steps:

### 1. Delete the CronJobs and Scripts

Navigate to the relevant folders and run the following commands to delete the CronJobs and scripts:

```bash
kubectl delete -f reduce-cpu-service-cronjob.yaml
kubectl delete -f reduce-cpu-service-script.yaml

kubectl delete -f reduce-mem-service-cronjob.yaml
kubectl delete -f reduce-mem-service-script.yaml

kubectl delete -f reduce-cpu-mem-service-cronjob.yaml
kubectl delete -f reduce-cpu-mem-service-script.yaml
```
