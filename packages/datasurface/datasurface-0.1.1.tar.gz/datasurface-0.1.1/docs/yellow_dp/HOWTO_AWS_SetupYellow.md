# HOWTO: Setup YellowDataPlatform on AWS EKS Environment

## Tip on how to use this document.

I (Billy) am testing this on my Macbook Pro with cursor and docker desktop installed. I typically use claude 4 sonnet and I ask Claude in Cursor to setup these environments following this document. Docker desktop is running and has kubernetes enabled. Open cursor and select this file in your edit window in cursor. Make a new AI chat, it should automatically add this file in the chat. Select the auto model. Use the following prompt to stand up your YellowDataPlatform environment.

```text
I have AWS CLI configured and want to deploy a YellowDataPlatform on AWS EKS. Please follow the instructions in @HOWTO_AWS_SetupYellow.md exactly. 

The GitHub PAT to use is:
put_your_git_pat_here

The PostgreSQL password to use is:
put_your_postgres_password_here

My AWS Account ID is:
put_your_aws_account_id_here

When creating the postgres secrets, please use the correct case as indicated in the HOWTO exactly.

We first need to rebuild the project docker container using buildx for multiplatform and pull it down on AWS before starting.
```

The first time you do this, it will download the different container images used (postgres/airflow/kafka/etc). This will take a couple of minutes. The AI usually sees this and automatically adds in waits for the containers to be ready.

The running environment takes just over 4GB of memory in docker. AWS EKS with EC2 node groups provides scalable compute, so resource allocation is automatic based on pod specifications.

## Overview

This document provides a step-by-step guide to set up a complete YellowDataPlatform environment on AWS EKS (Elastic Kubernetes Service). 

It is designed as an AI first document, easy to follow repeatedly by an AI assistant to speed installs. Tested in Cursor with a chat session with auto off and Claude 4 sonnet selected as the model.

The setup uses a two-ring approach:

- **Ring 0**: Generate bootstrap artifacts (runs in Docker container)
- **Ring 1**: Deploy to AWS EKS with full infrastructure (requires secrets and EKS cluster)

## Expected topology

### Database storage

There will be 1 or 2 RDS preexisting databases. One is used for Airflow and the other is the Datasurface merge database. The merge database will hold all the data for the system.

### Git clone cache

There will be an EFS file system which is used for shared storage between jobs/pods in the EKS cluster. The primary use case is for a git repoistory cache. Data surface caches the model repository in this shared storage. It's typically updated after 5 minutes of staleness.

### Airflow

There will be an Airflow web server and an airflow scheduler each running in their own pod within EKS. The resource limits of these pods are specified in the model but these model settings are only used for the initial setup. Once setup is complete, the devops team can modify these as needed.

### DataSurface jobs

These run within their own pods in EKS. They are launched from the Airflow scheduler pod. These jobs are responsible for:

* Keeping the DAGs up to date as the model changes.
* Ingesting and merging data from producer data sources which is needed by the consumers in the model.
* Executing DataTransformers which are required by the consumers in the model.
* Reconciling views for Workspaces.

### Credential management

All secrets are stored in AWS Secrets manager. The credentials are stored in a tree structure like this:

* datasurface/merge/credentials
* datasurface/git/credentials
* datasurface/sources/{source_type}/{source_name}'

Source credentials for sql databases use a source_type or 'sql_source'. The source_name is the DataContainer name for ingestion.

The airflow service account HAS access to EVERY credential in this tree. Airflow does not run any user code. The airflow DAGs expose the required secrets to the jobs running in the pods only. DataTransformers do run user code and only have secrets to read the views for their Workspace and to write to the output tables for their output Datastore.

## Prerequisites

This setup requires **Docker** and **AWS CLI** to be installed and configured on your system. The environment variable detection and configuration parsing uses the `datasurface/datasurface:latest` Docker image to ensure consistent Python dependencies and module availability.

**Required Tools:**
- Docker Desktop or Docker Engine
- AWS CLI configured with appropriate credentials
- kubectl configured for EKS cluster access
- GitHub repository with your datasurface ecosystem model
- GitHub Personal Access Token with repository access

**AWS Requirements:**
- AWS Account with EKS permissions
- IAM roles for EKS cluster and node groups
- VPC with public and private subnets
- ECR repository access for custom images
- **Two existing RDS PostgreSQL instances**:
  - **Airflow Database**: For Airflow metadata and DAG state
  - **Merge/Source Database**: For DataSurface merge operations and source data
  - These can be the same database or different databases.

**Docker Commands Used:**
- The setup automatically detects database configuration from your `eco.py` file using Docker containers
- All Python-based configuration parsing runs inside `datasurface/datasurface:latest` containers
- Ensure Docker is running before starting the setup process
- **Note**: The Docker commands assume you're running from a directory containing both `eco.py` and the `datasurface` source code

## Database Configuration Support

This document supports **external** PostgreSQL database configurations optimized for AWS:

### External PostgreSQL (YellowAWSExternalDatabaseAssembly)
- **Description**: Uses existing AWS RDS PostgreSQL databases (pre-provisioned)
- **Performance**: High performance (AWS-optimized instances, automated backups)
- **Use Case**: Production, performance testing, enterprise deployments with existing infrastructure
- **Configuration**: Database host/port for existing RDS instances extracted from `eco.py`, credentials managed via AWS Secrets Manager
- **Detection**: Automatically detected when `eco.py` uses `YellowAWSExternalDatabaseAssembly`
- **Credentials**: Username/password for existing RDS instances stored in AWS Secrets Manager, accessed via IRSA (IAM Roles for Service Accounts)
- **Prerequisites**: Two existing RDS PostgreSQL instances (one for Airflow, one for merge/source data)

The document automatically detects which configuration is being used and adjusts all commands accordingly.

## Phase 1: AWS Infrastructure Setup

### Step 1: Deploy AWS Infrastructure in Two Stages

To ensure a repeatable setup, we deploy the infrastructure in two stages: first the EKS cluster, then the IAM roles that depend on it.

**Stage 1: Deploy EKS Cluster and OIDC Provider**

This first stack provisions the core EKS cluster and creates the OIDC provider that the IAM roles will trust.

```bash
# Set your deployment parameters
export STACK_NAME="ds-eks-m5-v4" # Use a short, unique name, if it's too long then some S3 63 character limit issues will occur.
export KEY_PAIR_NAME="your-ec2-keypair-name"
export DATABASE_PASSWORD="your-secure-database-password"
export GITHUB_TOKEN="your-github-personal-access-token"

# Deploy the main EKS infrastructure stack
aws cloudformation create-stack \
  --stack-name $STACK_NAME \
  --template-body file://aws-marketplace/cloudformation/datasurface-eks-stack.yaml \
  --parameters \
    ParameterKey=KeyPairName,ParameterValue=$KEY_PAIR_NAME \
    ParameterKey=DatabasePassword,ParameterValue=$DATABASE_PASSWORD \
    ParameterKey=GitHubToken,ParameterValue=$GITHUB_TOKEN \
    ParameterKey=CreateDatabase,ParameterValue=false \
    ParameterKey=KubernetesDeploymentType,ParameterValue=EKS-EC2 \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

# Wait for the EKS stack to complete
echo "Waiting for EKS cluster stack to complete... (This will take 10-15 minutes)"
aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region us-east-1
echo "✅ EKS cluster stack created successfully."
```

**Stage 2: Deploy IAM Roles for Service Accounts**

Now that the cluster and OIDC provider exist, we deploy a second stack that creates the IAM roles for the EFS CSI Driver and Airflow.

```bash
# Get the OIDC Provider ARN from the first stack's outputs
export OIDC_PROVIDER_ARN=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query "Stacks[0].Outputs[?OutputKey=='EKSOIDCProviderArn'].OutputValue" \
  --output text \
  --region us-east-1)

echo "OIDC Provider ARN: $OIDC_PROVIDER_ARN"

# Deploy the IAM roles stack
aws cloudformation create-stack \
  --stack-name "${STACK_NAME}-iam-roles" \
  --template-body file://aws-marketplace/cloudformation/iam-roles-for-eks.yaml \
  --parameters \
    ParameterKey=EKSOIDCProviderArn,ParameterValue=$OIDC_PROVIDER_ARN \
    ParameterKey=StackName,ParameterValue=$STACK_NAME \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

# Wait for the IAM roles stack to complete
echo "Waiting for IAM roles stack to complete..."
aws cloudformation wait stack-create-complete --stack-name "${STACK_NAME}-iam-roles" --region us-east-1
echo "✅ IAM roles created successfully."

# CRITICAL: Fix OIDC trust policies (required due to hardcoded OIDC IDs in template)
echo "Fixing OIDC trust policies for both EFS and Airflow roles..."

# Extract OIDC issuer from provider ARN
OIDC_ISSUER=$(echo $OIDC_PROVIDER_ARN | cut -d'/' -f2-)

# Fix EFS CSI driver role trust policy
EFS_ROLE_ARN=$(aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}-iam-roles" \
  --query 'Stacks[0].Outputs[?OutputKey==`EFSCSIDriverRoleArn`].OutputValue' \
  --output text \
  --region us-east-1)
EFS_ROLE_NAME=$(echo $EFS_ROLE_ARN | cut -d'/' -f2)

cat > efs-trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "$OIDC_PROVIDER_ARN"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "${OIDC_ISSUER}:sub": "system:serviceaccount:kube-system:efs-csi-controller-sa",
                    "${OIDC_ISSUER}:aud": "sts.amazonaws.com"
                }
            }
        }
    ]
}
EOF

aws iam update-assume-role-policy --role-name $EFS_ROLE_NAME --policy-document file://efs-trust-policy.json

# Fix Airflow secrets role trust policy
cat > airflow-trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "$OIDC_PROVIDER_ARN"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "${OIDC_ISSUER}:sub": "system:serviceaccount:ns-yellow-starter:airflow-service-account",
                    "${OIDC_ISSUER}:aud": "sts.amazonaws.com"
                }
            }
        }
    ]
}
EOF

aws iam update-assume-role-policy --role-name airflow-secrets-role --policy-document file://airflow-trust-policy.json

echo "✅ OIDC trust policies fixed for both EFS and Airflow roles"
```

**Note**: This template creates:
- EKS cluster (v1.32) with EC2 node groups
- EFS file system for shared storage
- OIDC identity provider for IRSA
- IAM roles for EFS CSI driver and Airflow Secrets Manager access
- VPC with public/private subnets
- Application Load Balancer
- S3 bucket for artifacts

**⚠️ IMPORTANT - IAM Permissions Required**: The `datasurface_test` user needs these IAM permissions for CloudFormation to succeed:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:CreateOpenIDConnectProvider",
                "iam:CreateRole",
                "iam:PutRolePolicy",
                "iam:AttachRolePolicy",
                "iam:TagOpenIDConnectProvider",
                "iam:UpdateAssumeRolePolicy"
            ],
            "Resource": "*"
        }
    ]
}
```

**Solution**: Add these permissions to the `datasurface_test` group as an inline policy. The two-stage deployment creates all required IAM resources, but the trust policies may need manual fixing (see EFS CSI driver troubleshooting section).

**Instance Type Considerations**:
- Default `m5.large` (2 vCPU) may be insufficient for default Airflow resource requests
- Recommended: `m5.xlarge` (4 vCPU) or larger for production deployments
- See troubleshooting section for CPU resource issues

**Wait for Stack Creation:**
```bash
# Get the EKS cluster name from stack outputs
export CLUSTER_NAME=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`EKSClusterName`].OutputValue' \
  --output text \
  --region us-east-1)

echo "EKS Cluster Name: $CLUSTER_NAME"

# If you created Aurora, get the database connection details
if aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`AuroraClusterEndpoint`]' --output text --region us-east-1 > /dev/null 2>&1; then
  export AURORA_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`AuroraClusterEndpoint`].OutputValue' \
    --output text \
    --region us-east-1)
  
  export AURORA_PORT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`AuroraClusterPort`].OutputValue' \
    --output text \
    --region us-east-1)
  
  echo "Aurora Endpoint: $AURORA_ENDPOINT:$AURORA_PORT"
  echo "Aurora Username: postgres"
  echo "Aurora Password: [as specified in CloudFormation parameters]"
fi
```

### Step 2: Configure local kubectl for EKS and Setup EFS Storage

**Update kubeconfig to access the EKS cluster:**
```bash
# Configure kubectl for EKS cluster
aws eks update-kubeconfig \
  --region us-east-1 \
  --name $CLUSTER_NAME

# Verify cluster access
kubectl get nodes
kubectl get namespaces

# Install EFS CSI Driver (required for EFS storage)
aws eks create-addon \
  --cluster-name $CLUSTER_NAME \
  --addon-name aws-efs-csi-driver \
  --region us-east-1

# Install AWS Secrets Store CSI Driver (not available as addon in K8s 1.32)
echo "Installing Secrets Store CSI Driver via Helm..."
helm repo add secrets-store-csi-driver https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts
helm install csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver --namespace kube-system

# Install AWS provider for Secrets Store CSI Driver
kubectl apply -f https://raw.githubusercontent.com/aws/secrets-store-csi-driver-provider-aws/main/deployment/aws-provider-installer.yaml

# Wait for CSI drivers to be ready
aws eks wait addon-active \
  --cluster-name $CLUSTER_NAME \
  --addon-name aws-efs-csi-driver \
  --region us-east-1

echo "Waiting for Secrets Store CSI Driver to be ready..."
kubectl wait --for=condition=ready pod -l app=csi-secrets-store-provider-aws -n kube-system --timeout=60s

echo "EFS and Secrets Store CSI Drivers installed successfully"

# Get EFS details from CloudFormation outputs
export EFS_FILE_SYSTEM_ID=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`EFSFileSystemId`].OutputValue' \
  --output text \
  --region us-east-1)

export EFS_CSI_DRIVER_ROLE_ARN=$(aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}-iam-roles" \
  --query 'Stacks[0].Outputs[?OutputKey==`EFSCSIDriverRoleArn`].OutputValue' \
  --output text \
  --region us-east-1)

echo "EFS File System ID: $EFS_FILE_SYSTEM_ID"
echo "EFS CSI Driver Role ARN: $EFS_CSI_DRIVER_ROLE_ARN"

# Annotate EFS CSI controller service account with IAM role (for IRSA)
kubectl annotate serviceaccount efs-csi-controller-sa \
  -n kube-system \
  eks.amazonaws.com/role-arn=$EFS_CSI_DRIVER_ROLE_ARN \
  --overwrite

# Restart EFS CSI controller to pick up the new IAM role
kubectl rollout restart deployment/efs-csi-controller -n kube-system

# Wait for EFS CSI controller to be ready
kubectl rollout status deployment/efs-csi-controller -n kube-system

# Create EFS StorageClass manifest
cat > efs-storageclass.yaml << EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: efs-sc
  annotations:
    storageclass.kubernetes.io/is-default-class: "false"
provisioner: efs.csi.aws.com
parameters:
  provisioningMode: efs-ap
  fileSystemId: $EFS_FILE_SYSTEM_ID
  directoryPerms: "0755"
  uid: "50000"
  gid: "50000"
volumeBindingMode: Immediate
allowVolumeExpansion: false
EOF

# Apply the EFS StorageClass
kubectl apply -f efs-storageclass.yaml

# Verify StorageClass creation
kubectl get storageclass efs-sc

# Test EFS provisioning with a simple PVC (catch trust policy issues early)
cat > test-efs-pvc.yaml << EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-efs-pvc
  namespace: default
spec:
  storageClassName: efs-sc
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
EOF

kubectl apply -f test-efs-pvc.yaml
echo "Waiting 30 seconds to test EFS provisioning..."
sleep 30

# Check if test PVC binds successfully
PVC_STATUS=$(kubectl get pvc test-efs-pvc -o jsonpath='{.status.phase}')
if [ "$PVC_STATUS" = "Bound" ]; then
    echo "✅ EFS provisioning test successful"
    kubectl delete pvc test-efs-pvc
    rm test-efs-pvc.yaml
else
    echo "❌ EFS provisioning failed - check trust policy (see troubleshooting section)"
    kubectl describe pvc test-efs-pvc
    echo "Run the EFS CSI driver trust policy fix from the troubleshooting section"
fi

echo "EFS StorageClass created successfully"
```

### Step 3: Configure Airflow Service Account with IAM Role

**CRITICAL**: After deploying the IAM roles stack, you must update the Airflow service account annotation with the correct IAM role ARN.

```bash
# Get the Airflow IAM role ARN from the IAM roles stack
export AIRFLOW_ROLE_ARN=$(aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}-iam-roles" \
  --query 'Stacks[0].Outputs[?OutputKey==`AirflowSecretsRoleArn`].OutputValue' \
  --output text \
  --region us-east-1)

echo "Airflow IAM Role ARN: $AIRFLOW_ROLE_ARN"

# Update the service account annotation (this will be needed after deploying Airflow)
# Note: This step is done after deploying the Kubernetes artifacts in the next phase
echo "Save this ARN - you'll need it after deploying Airflow artifacts"
```

### Step 4: Create AWS Secrets Manager Secrets

**Choose based on your database setup:**

**Option A: Using New Aurora PostgreSQL Cluster**
```bash
# ✅ Database credentials are automatically created by CloudFormation!
# The following secrets are automatically created when Aurora is deployed:
# - datasurface/merge/credentials
# - datasurface/airflow/credentials  
# - datasurface/sources/store1/credentials

# Verify the secrets were created automatically
aws secretsmanager list-secrets \
  --query 'SecretList[?contains(Name, `datasurface`)].Name' \
  --output table \
  --region us-east-1

echo "✅ Database credentials automatically created by CloudFormation"
```

**Option B: Using Existing RDS Instances**

**Create database and Git credentials in AWS Secrets Manager for your existing RDS instances:**

**⚠️ IMPORTANT**: Use URI format for Airflow database connection (for CSI driver mounting):

```bash
# Create Airflow database connection (mounted as file via AWS Secrets Store CSI driver)
aws secretsmanager create-secret \
  --name "airflow/connections/postgres_default" \
  --description "Airflow database connection for existing RDS (CSI mounted)" \
  --secret-string "postgresql://postgres:your-existing-rds-password@aws-postgres-1.ceziu2wcs0eo.us-east-1.rds.amazonaws.com:5432/airflow_db" \
  --region us-east-1

# Create merge database credentials (for DataSurface jobs - still uses JSON format)
aws secretsmanager create-secret \
  --name "datasurface/merge/credentials" \
  --description "DataSurface merge database credentials for existing RDS" \
  --secret-string '{"postgres_USER":"postgres","postgres_PASSWORD":"your-existing-rds-password"}' \
  --region us-east-1

# Create source database credentials (example for Store1)
aws secretsmanager create-secret \
  --name "datasurface/sources/store1/credentials" \
  --description "DataSurface Store1 source database credentials for existing RDS" \
  --secret-string '{"store1_USER":"postgres","store1_PASSWORD":"your-existing-rds-password"}' \
  --region us-east-1

# Create Git credentials
aws secretsmanager create-secret \
  --name "datasurface/git/credentials" \
  --description "DataSurface Git repository credentials" \
  --secret-string '{"token":"your-github-personal-access-token"}' \
  --region us-east-1

# Verify secrets were created
aws secretsmanager list-secrets \
  --query 'SecretList[?contains(Name, `datasurface`) || contains(Name, `airflow`)].Name' \
  --output table \
  --region us-east-1
```

**Key Format Differences:**
- **Airflow database connection**: Use PostgreSQL URI string for file-based reading via CSI driver (e.g., `postgresql://user:pass@host:port/db`)
- **DataSurface jobs**: Use JSON format for boto3 fetching in DAG code  
- **Both approaches**: Use IRSA for secure access without storing AWS credentials

**Critical Configuration Notes:**
- **Secret Name**: Must be exactly `airflow/connections/postgres_default` for CSI driver mounting
- **Secret Format**: PostgreSQL URI string for direct file reading (e.g., `postgresql://user:pass@host:port/db`)
- **ConfigMap Database Section**: Uses `sql_alchemy_conn = file:///mnt/secrets/airflow-db-connection` for reliable file-based connection
- **CSI Driver**: AWS Secrets Store CSI driver mounts secret as file, eliminating API call timeouts during initialization

**Create Git credentials (required for both options):**
```bash
# Create Git credentials (this is always required)
aws secretsmanager create-secret \
  --name "datasurface/git/credentials" \
  --description "DataSurface Git repository credentials" \
  --secret-string "{\"token\":\"your-github-personal-access-token\"}" \
  --region us-east-1

# Verify all secrets are available
aws secretsmanager list-secrets \
  --query 'SecretList[?contains(Name, `datasurface`)].Name' \
  --output table \
  --region us-east-1
```

**Important Notes:**
- **For Aurora option**: All databases initially use the same Aurora cluster with separate database names
- **For existing RDS**: Replace credentials with your actual RDS instance credentials
- **Network access**: Ensure EKS cluster can reach your databases (Aurora is automatically configured in same VPC)
- **Security**: Use strong passwords and rotate them regularly

## Phase 2: Bootstrap Artifact Generation (Ring 0)

### Step 1: Clone the Starter Repository

**Optional: Remove Previous Environment**
If you have an existing yellow_aws_dual_aurora deployment, clean it up first:
```bash
# Remove old Kubernetes namespace and all resources
kubectl delete namespace "$NAMESPACE"

# Remove local artifacts (if reusing same directory)
rm -rf yellow_aws_dual_aurora/generated_output/
```

**Clone Fresh Repository**
```bash
git clone https://github.com/billynewport/yellow_aws_dual_aurora.git
cd yellow_aws_dual_aurora
```

### Step 2: Build and Push Custom Airflow Image (REQUIRED)

**CRITICAL**: The YellowDataPlatform uses a custom Airflow image with database drivers and AWS dependencies. This image must be built and pushed before deployment.

```bash
# Build and push multiplatform custom Airflow image
cd /path/to/datasurface
docker buildx build --platform linux/amd64,linux/arm64 \
  -f src/datasurface/platforms/yellow/docker/Docker.airflow_with_drivers \
  -t datasurface/airflow:2.11.0 \
  --push .

# Verify the image includes AWS dependencies
docker run --rm datasurface/airflow:2.11.0 pip list | grep -E "(boto3|apache-airflow-providers-amazon|apache-airflow-providers-cncf-kubernetes)"
```

**Why This Is Required:**
- The generated Kubernetes YAML references `datasurface/airflow:2.11.0`
- This custom image includes PostgreSQL, MSSQL, Oracle, and DB2 drivers
- **AWS-specific**: Includes `boto3`, `apache-airflow-providers-amazon`, and `apache-airflow-providers-cncf-kubernetes`
- Without this step, Airflow pods will fail with missing AWS SDK dependencies

### Step 3: Configure the Ecosystem Model and Detect Database Configuration

```bash
# Review the ecosystem model
cat eco.py

# Review the platform assignments file (should already exist with correct format)
cat dsg_platform_mapping.json
```

**Expected format for dsg_platform_mapping.json:**
```json
[
  {
    "dsgName": "LiveDSG",
    "workspace": "Consumer1",
    "assignments": [
      {
        "dataPlatform": "YellowLive",
        "documentation": "Live Yellow DataPlatform",
        "productionStatus": "PRODUCTION",
        "deprecationsAllowed": "NEVER",
        "status": "PROVISIONED"
      }
    ]
  },
  {
    "dsgName": "ForensicDSG", 
    "workspace": "Consumer1",
    "assignments": [
      {
        "dataPlatform": "YellowForensic",
        "documentation": "Forensic Yellow DataPlatform", 
        "productionStatus": "PRODUCTION",
        "deprecationsAllowed": "NEVER",
        "status": "PROVISIONED"
      }
    ]
  }
]
```

**Key configurations to verify:**
- DataPlatform names and credentials
- AWS RDS hostname and port configuration
- Merge database name specification
- Datastore connection details
- Workspace and DatasetGroup configurations
- **AWS-specific**: Ensure `YellowAWSExternalDatabaseAssembly` is used for AWS RDS integration

**Note:** Database configuration detection and environment variable setup is now handled by the utility scripts in Step 4.

### Step 4: Create Environment Setup and Utility Scripts (AWS-Specific)

To avoid shell escaping issues and improve reliability, create these utility scripts in your `yellow_aws_dual_aurora` directory:

**Create AWS Environment Setup Script (`setup_aws_env.sh`):**

```bash
# Create the AWS environment setup script locally
cat > setup_aws_env.sh << 'EOF'
#!/bin/bash

# YellowDataPlatform AWS Environment Setup Script
echo "=== YellowDataPlatform AWS Environment Setup ==="

# Set basic variables for existing RDS instances
export MERGE_PG_PASSWORD="your-existing-rds-password"
export MERGE_PG_USER="your-existing-rds-username"
export AIRFLOW_PG_PASSWORD="your-existing-airflow-rds-password"
export AIRFLOW_PG_USER="your-existing-airflow-rds-username"
export NAMESPACE="ns-yellow-starter"
export MERGE_DB_NAME="datasurface_merge"
export EXTERNAL_DB="true"
export AWS_ACCOUNT_ID="your-aws-account-id"

# Detect database configuration from eco.py
if grep -q "YellowAWSExternalDatabaseAssembly" eco.py; then
    echo "=== AWS External PostgreSQL Database Configuration Detected ==="
    
    # Extract merge database host (existing RDS instance)
    MERGE_PG_HOST=$(docker run --rm -v "$(pwd):/workspace" -w /workspace datasurface/datasurface:latest python3 -c "
import sys
sys.path.append('.')
import eco
ecosystem = eco.createEcosystem()
psp = None
for p in ecosystem.platformServicesProviders:
    if hasattr(p, 'mergeStore'):
        psp = p
        break
if psp and hasattr(psp.mergeStore, 'hostPortPair'):
    print(psp.mergeStore.hostPortPair.hostName)
else:
    print('your-existing-merge-rds-endpoint.region.rds.amazonaws.com')
")
    
    # Extract merge database port
    MERGE_PG_PORT=$(docker run --rm -v "$(pwd):/workspace" -w /workspace datasurface/datasurface:latest python3 -c "
import sys
sys.path.append('.')
import eco
ecosystem = eco.createEcosystem()
psp = None
for p in ecosystem.platformServicesProviders:
    if hasattr(p, 'mergeStore'):
        psp = p
        break
if psp and hasattr(psp.mergeStore, 'hostPortPair'):
    print(psp.mergeStore.hostPortPair.port)
else:
    print('5432')
")

    # Extract Airflow database host (existing RDS instance)
    AIRFLOW_PG_HOST=$(docker run --rm -v "$(pwd):/workspace" -w /workspace datasurface/datasurface:latest python3 -c "
import sys
sys.path.append('.')
import eco
ecosystem = eco.createEcosystem()
psp = None
for p in ecosystem.platformServicesProviders:
    if hasattr(p, 'airflowStore') or hasattr(p, 'db'):
        psp = p
        break
if psp and hasattr(psp, 'db') and hasattr(psp.db, 'hostPortPair'):
    print(psp.db.hostPortPair.hostName)
else:
    print('your-existing-airflow-rds-endpoint.region.rds.amazonaws.com')
")

    # Extract Airflow database port
    AIRFLOW_PG_PORT=$(docker run --rm -v "$(pwd):/workspace" -w /workspace datasurface/datasurface:latest python3 -c "
import sys
sys.path.append('.')
import eco
ecosystem = eco.createEcosystem()
psp = None
for p in ecosystem.platformServicesProviders:
    if hasattr(p, 'airflowStore') or hasattr(p, 'db'):
        psp = p
        break
if psp and hasattr(psp, 'db') and hasattr(psp.db, 'hostPortPair'):
    print(psp.db.hostPortPair.port)
else:
    print('5432')
")
    
    export MERGE_PG_HOST MERGE_PG_PORT AIRFLOW_PG_HOST AIRFLOW_PG_PORT
    EXTERNAL_DB=true
    
else
    echo "=== ERROR: AWS deployment requires YellowAWSExternalDatabaseAssembly ==="
    echo "Please update eco.py to use YellowAWSExternalDatabaseAssembly for AWS RDS integration"
    exit 1
fi

# Export all variables
export MERGE_PG_HOST MERGE_PG_PORT MERGE_PG_USER MERGE_PG_PASSWORD AIRFLOW_PG_HOST AIRFLOW_PG_PORT AIRFLOW_PG_USER AIRFLOW_PG_PASSWORD EXTERNAL_DB NAMESPACE MERGE_DB_NAME AWS_ACCOUNT_ID

echo "Environment Variables Set:"
echo "  MERGE_PG_HOST=$MERGE_PG_HOST (Merge/Source RDS)"
echo "  MERGE_PG_PORT=$MERGE_PG_PORT"
echo "  MERGE_PG_USER=$MERGE_PG_USER"
echo "  AIRFLOW_PG_HOST=$AIRFLOW_PG_HOST (Airflow RDS)"
echo "  AIRFLOW_PG_PORT=$AIRFLOW_PG_PORT"
echo "  AIRFLOW_PG_USER=$AIRFLOW_PG_USER"
echo "  NAMESPACE=$NAMESPACE"
echo "  MERGE_DB_NAME=$MERGE_DB_NAME"
echo "  EXTERNAL_DB=$EXTERNAL_DB"
echo "  AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID"

# Save to env file for sourcing
cat > .env << ENVEOF
export MERGE_PG_HOST="$MERGE_PG_HOST"
export MERGE_PG_PORT="$MERGE_PG_PORT"
export MERGE_PG_USER="$MERGE_PG_USER"
export MERGE_PG_PASSWORD="$MERGE_PG_PASSWORD"
export AIRFLOW_PG_HOST="$AIRFLOW_PG_HOST"
export AIRFLOW_PG_PORT="$AIRFLOW_PG_PORT"
export AIRFLOW_PG_USER="$AIRFLOW_PG_USER"
export AIRFLOW_PG_PASSWORD="$AIRFLOW_PG_PASSWORD"
export NAMESPACE="$NAMESPACE"
export MERGE_DB_NAME="$MERGE_DB_NAME"
export EXTERNAL_DB="$EXTERNAL_DB"
export AWS_ACCOUNT_ID="$AWS_ACCOUNT_ID"
ENVEOF

echo "Environment variables saved to .env file"
echo "To use in future sessions: source .env"
EOF

chmod +x setup_aws_env.sh
```

**Create AWS Utility Script (`aws_utils.sh`):**
```bash
cat > aws_utils.sh << 'EOF'
#!/bin/bash

# YellowDataPlatform AWS Utility Script
source .env 2>/dev/null || { echo "Please run ./setup_aws_env.sh first"; exit 1; }

case "$1" in
    "status")
        echo "=== Pod Status ==="
        kubectl get pods -n "$NAMESPACE"
        echo ""
        echo "=== Recent Events ==="
        kubectl get events -n "$NAMESPACE" --sort-by=.metadata.creationTimestamp | tail -5
        ;;
    "logs")
        echo "=== Airflow Scheduler Logs (last 50 lines) ==="
        kubectl logs deployment/airflow-scheduler -n "$NAMESPACE" --tail=50
        ;;
        
    "dags")
        echo "=== Airflow DAGs ==="
        kubectl exec deployment/airflow-scheduler -n "$NAMESPACE" -- airflow dags list
        ;;
        
    "db-test")
        echo "=== Testing AWS RDS Database Connections ==="
        echo "Testing Merge/Source RDS..."
        kubectl run db-test-merge --rm -i --restart=Never \
          --image=postgres:16 \
          --env="PGPASSWORD=$MERGE_PG_PASSWORD" \
          -n "$NAMESPACE" \
          -- psql -h "$MERGE_PG_HOST" -p "$MERGE_PG_PORT" -U "$MERGE_PG_USER" -c "SELECT 'Merge RDS' as instance, version();"
        
        echo "Testing Airflow RDS..."
        kubectl run db-test-airflow --rm -i --restart=Never \
          --image=postgres:16 \
          --env="PGPASSWORD=$AIRFLOW_PG_PASSWORD" \
          -n "$NAMESPACE" \
          -- psql -h "$AIRFLOW_PG_HOST" -p "$AIRFLOW_PG_PORT" -U "$AIRFLOW_PG_USER" -c "SELECT 'Airflow RDS' as instance, version();"
        ;;
        
    "db-list")
        echo "=== Listing Databases on AWS RDS Instances ==="
        echo "Merge/Source RDS databases:"
        kubectl run db-list-merge --rm -i --restart=Never \
          --image=postgres:16 \
          --env="PGPASSWORD=$MERGE_PG_PASSWORD" \
          -n "$NAMESPACE" \
          -- psql -h "$MERGE_PG_HOST" -p "$MERGE_PG_PORT" -U "$MERGE_PG_USER" -c "SELECT datname FROM pg_database;"
        
        echo "Airflow RDS databases:"
        kubectl run db-list-airflow --rm -i --restart=Never \
          --image=postgres:16 \
          --env="PGPASSWORD=$AIRFLOW_PG_PASSWORD" \
          -n "$NAMESPACE" \
          -- psql -h "$AIRFLOW_PG_HOST" -p "$AIRFLOW_PG_PORT" -U "$AIRFLOW_PG_USER" -c "SELECT datname FROM pg_database;"
        ;;
        
    "secrets-test")
        echo "=== Testing AWS Secrets Manager Access ==="
        kubectl run secrets-test --rm -i --restart=Never \
          --image=amazon/aws-cli:latest \
          --env="AWS_REGION=us-east-1" \
          -n "$NAMESPACE" \
          -- aws secretsmanager list-secrets --query 'SecretList[?contains(Name, `datasurface`)].Name' --output table
        ;;
        
    "port-forward")
        echo "=== Setting up port forwarding for Airflow UI ==="
        echo "Access Airflow at http://localhost:8080"
        echo "Username: admin"
        echo "Password: admin123"
        kubectl port-forward svc/airflow-webserver-service 8080:8080 -n "$NAMESPACE"
        ;;
        
    *)
        echo "YellowDataPlatform AWS Utility Script"
        echo "Usage: $0 {status|logs|dags|db-test|db-list|secrets-test|port-forward}"
        echo ""
        echo "Commands:"
        echo "  status       - Show pod status and recent events"
        echo "  logs         - Show Airflow scheduler logs"
        echo "  dags         - List Airflow DAGs"
        echo "  db-test      - Test AWS RDS database connection"
        echo "  db-list      - List databases on AWS RDS"
        echo "  secrets-test - Test AWS Secrets Manager access"
        echo "  port-forward - Set up port forwarding for Airflow UI"
        ;;
esac
EOF

chmod +x aws_utils.sh
```

**Run the AWS Environment Setup:**
```bash
# Update the script with your actual values first
sed -i 's/your-existing-rds-password/actual-merge-rds-password/g' setup_aws_env.sh
sed -i 's/your-existing-rds-username/actual-merge-rds-username/g' setup_aws_env.sh
sed -i 's/your-existing-airflow-rds-password/actual-airflow-rds-password/g' setup_aws_env.sh
sed -i 's/your-existing-airflow-rds-username/actual-airflow-rds-username/g' setup_aws_env.sh
sed -i 's/your-aws-account-id/123456789012/g' setup_aws_env.sh

# Run the setup script to detect configuration and set environment variables
./setup_aws_env.sh
```

### Step 5: Generate Bootstrap Artifacts

It's important to use the correct docker image, especially when developing. Kubernetes and docker use DIFFERENT container caches. You need to docker pull the container image before running this command.

```bash
# Generate artifacts for both platforms
docker run --rm \
  -v "$(pwd)":/workspace/model \
  -w /workspace/model \
  datasurface/datasurface:latest \
  python -m datasurface.cmd.platform generatePlatformBootstrap \
  --ringLevel 0 \
  --model /workspace/model \
  --output /workspace/model/generated_output \
  --psp Test_DP
```

### Step 6: Verify Generated Artifacts

```bash
# Check the generated files
ls -la generated_output/Test_DP/
```

**Expected artifacts for PSP (Test_DP):**
- `kubernetes-bootstrap.yaml` - Kubernetes deployment configuration (AWS EKS optimized)
- `test_dp_infrastructure_dag.py` - Platform management DAG (with AWS Secrets Manager integration)
- `test_dp_model_merge_job.yaml` - Model merge job for populating ingestion stream configurations
- `test_dp_ring1_init_job.yaml` - Ring 1 initialization job for creating database schemas
- `test_dp_reconcile_views_job.yaml` - Workspace views reconciliation job

## Phase 3: AWS EKS Infrastructure Setup (Ring 1)

### Step 1: Create Kubernetes Namespace

**Using Environment Variables from Setup Script:**
```bash
# Source environment variables (if not already loaded)
source .env

# Create namespace
kubectl create namespace "$NAMESPACE"

# Verify namespace creation
kubectl get namespaces | grep "$NAMESPACE"
```

**Note**: AWS Secrets Manager integration eliminates the need for Kubernetes secrets. Credentials are fetched directly from AWS Secrets Manager using IRSA (IAM Roles for Service Accounts).

### Step 2: Create Required Databases and Deploy Infrastructure

**IMPORTANT**: The deployment order has been updated based on real-world testing. Infrastructure must be deployed BEFORE Ring 1 initialization because Ring 1 jobs require PVCs that are created by the infrastructure deployment.

**Updated AWS Deployment Order:**
1. Create and initialize AWS RDS databases
2. Deploy Kubernetes infrastructure (creates required PVCs and IRSA)
3. Run Ring 1 initialization (requires PVCs to exist)
4. Initialize Airflow and deploy DAGs

```bash
# Source environment variables
source .env

# Create databases on existing AWS RDS instances
echo "=== Creating Databases on Existing AWS RDS Instances ==="

# First, terminate any existing connections and drop databases on Merge RDS
kubectl run db-drop-merge --rm -i --restart=Never \
  --image=postgres:16 \
  --env="PGPASSWORD=$MERGE_PG_PASSWORD" \
  -n "$NAMESPACE" \
  -- bash -c "
    # Terminate connections to databases on Merge RDS
    psql -h '$MERGE_PG_HOST' -p '$MERGE_PG_PORT' -U '$MERGE_PG_USER' -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname IN ('customer_db', '$MERGE_DB_NAME') AND pid <> pg_backend_pid();\" || echo 'No connections to terminate'
    # Drop databases on Merge RDS
    psql -h '$MERGE_PG_HOST' -p '$MERGE_PG_PORT' -U '$MERGE_PG_USER' -c 'DROP DATABASE IF EXISTS customer_db;'  
    psql -h '$MERGE_PG_HOST' -p '$MERGE_PG_PORT' -U '$MERGE_PG_USER' -c 'DROP DATABASE IF EXISTS $MERGE_DB_NAME;'
  "

# Terminate connections and drop databases on Airflow RDS
kubectl run db-drop-airflow --rm -i --restart=Never \
  --image=postgres:16 \
  --env="PGPASSWORD=$AIRFLOW_PG_PASSWORD" \
  -n "$NAMESPACE" \
  -- bash -c "
    # Terminate connections to databases on Airflow RDS
    psql -h '$AIRFLOW_PG_HOST' -p '$AIRFLOW_PG_PORT' -U '$AIRFLOW_PG_USER' -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'airflow_db' AND pid <> pg_backend_pid();\" || echo 'No connections to terminate'
    # Drop database on Airflow RDS
    psql -h '$AIRFLOW_PG_HOST' -p '$AIRFLOW_PG_PORT' -U '$AIRFLOW_PG_USER' -c 'DROP DATABASE IF EXISTS airflow_db;'
  "

# Create fresh databases on Merge RDS
kubectl run db-create-merge --rm -i --restart=Never \
  --image=postgres:16 \
  --env="PGPASSWORD=$MERGE_PG_PASSWORD" \
  -n "$NAMESPACE" \
  -- bash -c "
    psql -h '$MERGE_PG_HOST' -p '$MERGE_PG_PORT' -U '$MERGE_PG_USER' -c 'CREATE DATABASE customer_db;'  
    psql -h '$MERGE_PG_HOST' -p '$MERGE_PG_PORT' -U '$MERGE_PG_USER' -c 'CREATE DATABASE $MERGE_DB_NAME;'
  "

# Create fresh database on Airflow RDS
kubectl run db-create-airflow --rm -i --restart=Never \
  --image=postgres:16 \
  --env="PGPASSWORD=$AIRFLOW_PG_PASSWORD" \
  -n "$NAMESPACE" \
  -- bash -c "
    psql -h '$AIRFLOW_PG_HOST' -p '$AIRFLOW_PG_PORT' -U '$AIRFLOW_PG_USER' -c 'CREATE DATABASE airflow_db;'
  "

# Verify databases were created
./aws_utils.sh db-list

# Create source tables and initial test data using the data simulator
# This creates the customers and addresses tables with initial data and simulates some changes and leaves it running continuously.
kubectl run data-simulator --restart=Never \
  --image=datasurface/datasurface:latest \
  --env="POSTGRES_USER=$MERGE_PG_USER" \
  --env="POSTGRES_PASSWORD=$MERGE_PG_PASSWORD" \
  -n "$NAMESPACE" \
  -- python src/tests/data_change_simulator.py \
  --host "$MERGE_PG_HOST" \
  --port "$MERGE_PG_PORT" \
  --database customer_db \
  --user "$MERGE_PG_USER" \
  --password "$MERGE_PG_PASSWORD" \
  --create-tables \
  --max-changes 1000000 \
  --verbose &

# Wait a moment for the data simulator to start creating tables, then continue
echo "Data simulator started in background. Continuing with setup..."
echo "Note: The data simulator will run continuously for days, simulating ongoing data changes."
echo "You can monitor it with: kubectl logs data-simulator -n \$NAMESPACE -f"
sleep 10

# Deploy Kubernetes infrastructure FIRST (creates required PVCs and IRSA)
kubectl apply -f generated_output/Test_DP/kubernetes-bootstrap.yaml

# CRITICAL: Update Airflow service account with correct IAM role ARN
kubectl annotate serviceaccount airflow-service-account \
  -n "$NAMESPACE" \
  eks.amazonaws.com/role-arn=$AIRFLOW_ROLE_ARN \
  --overwrite

echo "✅ Airflow service account configured with IAM role: $AIRFLOW_ROLE_ARN"

# Now apply Ring 1 initialization job (requires PVCs created above)
kubectl apply -f generated_output/Test_DP/test_dp_ring1_init_job.yaml

# Wait for Ring 1 initialization to complete
kubectl wait --for=condition=complete job/test-dp-ring1-init -n "$NAMESPACE" --timeout=300s

# Check status
./aws_utils.sh status
```

### Step 3: Verify Infrastructure and Initialize Airflow

**Now that infrastructure is deployed and Ring 1 initialization is complete:**

```bash
# Verify infrastructure is running

# Verify AWS RDS database connectivity using utility script
./aws_utils.sh db-test

# Test AWS Secrets Manager access
./aws_utils.sh secrets-test

# Check deployment status
./aws_utils.sh status
```

### Step 4: Initialize Airflow Database and Services

**CRITICAL**: Airflow requires proper database initialization before the webserver can start. The AWS setup uses external RDS databases that must be initialized properly.

```bash
# Source environment variables
source .env

# Wait for Airflow scheduler to be ready (init container must complete first)
kubectl wait --for=condition=ready pod -l app=airflow-scheduler -n "$NAMESPACE" --timeout=600s

# Initialize Airflow database (the init container should have done this, but verify)
kubectl exec deployment/airflow-scheduler -n "$NAMESPACE" -- airflow db init

# Wait for Airflow webserver to be ready (after database initialization)
kubectl wait --for=condition=ready pod -l app=airflow-webserver -n "$NAMESPACE" --timeout=300s

# Verify Airflow database connection
kubectl exec deployment/airflow-scheduler -n "$NAMESPACE" -- airflow db check

# Check status using utility script
./aws_utils.sh status
```

### Step 5: Create Airflow Admin User

```bash
# Create Airflow admin user (required for web UI access)
kubectl exec deployment/airflow-scheduler -n "$NAMESPACE" -- \
  airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin123

echo "✅ Airflow admin user created: admin/admin123"
```

### Step 6: Deploy DAG Factory and Model Merge Jobs

```bash
# Get the current scheduler pod name
SCHEDULER_POD=$(kubectl get pods -n "$NAMESPACE" -l app=airflow-scheduler -o jsonpath='{.items[0].metadata.name}')

# Copy infrastructure DAG to Airflow
kubectl cp generated_output/Test_DP/test_dp_infrastructure_dag.py $SCHEDULER_POD:/opt/airflow/dags/ -n "$NAMESPACE"

# Deploy model merge job to populate ingestion stream configurations
kubectl apply -f generated_output/Test_DP/test_dp_model_merge_job.yaml

# Wait for model merge job to complete
kubectl wait --for=condition=complete job/test-dp-model-merge-job -n "$NAMESPACE" --timeout=300s

# Deploy reconcile views job to create/update workspace views
kubectl apply -f generated_output/Test_DP/test_dp_reconcile_views_job.yaml

# Wait for reconcile views job to complete
kubectl wait --for=condition=complete job/test-dp-reconcile-views-job -n "$NAMESPACE" --timeout=300s

# Restart Airflow scheduler to trigger factory DAGs (creates dynamic ingestion stream DAGs)
kubectl delete pod -n "$NAMESPACE" -l app=airflow-scheduler
kubectl wait --for=condition=ready pod -l app=airflow-scheduler -n "$NAMESPACE" --timeout=300s
```

### Step 7: Verify AWS Deployment

```bash
# Check all pods are running
./aws_utils.sh status

# Verify AWS RDS databases exist
./aws_utils.sh db-list

# Test AWS Secrets Manager integration
./aws_utils.sh secrets-test

# List all DAGs
./aws_utils.sh dags

# Access Airflow web interface (runs in foreground)
./aws_utils.sh port-forward
```

### Step 6: Deploy DAG Factory and Model Merge Jobs

```bash
# Get the current scheduler pod name
SCHEDULER_POD=$(kubectl get pods -n "$NAMESPACE" -l app=airflow-scheduler -o jsonpath='{.items[0].metadata.name}')

# Copy infrastructure DAG to Airflow
kubectl cp generated_output/Test_DP/test_dp_infrastructure_dag.py $SCHEDULER_POD:/opt/airflow/dags/ -n "$NAMESPACE"

# Deploy model merge job to populate ingestion stream configurations
kubectl apply -f generated_output/Test_DP/test_dp_model_merge_job.yaml

# Wait for model merge job to complete
kubectl wait --for=condition=complete job/test-dp-model-merge-job -n "$NAMESPACE" --timeout=300s

# Deploy reconcile views job to create/update workspace views
kubectl apply -f generated_output/Test_DP/test_dp_reconcile_views_job.yaml

# Wait for reconcile views job to complete
kubectl wait --for=condition=complete job/test-dp-reconcile-views-job -n "$NAMESPACE" --timeout=300s

# Restart Airflow scheduler to trigger factory DAGs (creates dynamic ingestion stream DAGs)
kubectl delete pod -n "$NAMESPACE" -l app=airflow-scheduler
kubectl wait --for=condition=ready pod -l app=airflow-scheduler -n "$NAMESPACE" --timeout=300s
```

### Step 7: Verify AWS Deployment

```bash
# Check all pods are running
./aws_utils.sh status

# Verify AWS RDS databases exist
./aws_utils.sh db-list

# Test AWS Secrets Manager integration
./aws_utils.sh secrets-test

# List all DAGs
./aws_utils.sh dags

# Access Airflow web interface (runs in foreground)
./aws_utils.sh port-forward
```

Open http://localhost:8080 and login with:
- **Username**: `admin`
- **Password**: `admin123`

**Expected DAGs in Airflow UI:**
- `test-dp_infrastructure` - Platform infrastructure management (paused by default)
- `yellowlive_factory_dag` - YellowLive platform factory (created dynamically)
- `yellowlive_datatransformer_factory` - YellowLive datatransformer factory (created dynamically, paused)
- `yellowforensic_factory_dag` - YellowForensic platform factory (created dynamically)
- `yellowforensic_datatransformer_factory` - YellowForensic datatransformer factory (created dynamically, paused)
- `yellowlive__Store1_ingestion` - YellowLive Store1 ingestion stream DAG (created dynamically)
- `yellowforensic__Store1_ingestion` - YellowForensic Store1 ingestion stream DAG (created dynamically)
- `yellowlive__MaskedStoreGenerator_datatransformer` - YellowLive DataTransformer execution DAG (created dynamically)
- `yellowforensic__MaskedStoreGenerator_datatransformer` - YellowForensic DataTransformer execution DAG (created dynamically)

## Ring Level Explanation

**Ring 0**: Generate artifacts only (no external dependencies)
- Creates Kubernetes YAML, DAG files, and job templates
- Requires no external services, runs in Docker container
- Generated artifacts are ready for direct deployment to AWS EKS
- **AWS-specific**: Includes IRSA annotations and AWS Secrets Manager integration

**Ring 1**: Initialize databases and runtime configuration (requires AWS EKS cluster)
- Creates platform-specific database schemas and configurations on AWS RDS
- Configures IRSA for AWS Secrets Manager access
- Sets up EKS-specific storage classes and networking

## AWS-Specific Features

**IAM Roles for Service Accounts (IRSA):**
- EFS CSI driver service account with IAM role for dynamic provisioning
- Airflow service account with IAM role for AWS Secrets Manager access
- Eliminates need for storing AWS credentials in pods
- Automatic credential rotation and fine-grained permissions

**AWS Secrets Manager Integration (Hybrid Approach):**
- **Airflow database connection**: Mounted as file via AWS Secrets Store CSI driver using URI format
- **Static secrets**: Core platform secrets (Airflow DB, Git) mounted as files for reliable startup
- **Dynamic secrets**: Source databases and job-specific credentials fetched via boto3 SDK in DAG code
- **Configuration**: Uses `sql_alchemy_conn = file:///mnt/secrets/airflow-db-connection` for reliable initialization
- **Security**: Uses IRSA (IAM Roles for Service Accounts) for both CSI driver and API access - no AWS credentials stored in pods

**EKS with EC2 Node Groups:**
- Managed Kubernetes control plane with AWS-optimized worker nodes
- Auto Scaling Groups for automatic node scaling
- Support for EFS CSI driver and privileged containers
- Cost-effective compute with reserved instance options

**AWS RDS Integration:**
- Managed PostgreSQL database service for Airflow and application data
- Automated backups, maintenance, and security patches
- High availability with Multi-AZ deployments
- Performance monitoring and optimization tools

**Amazon EFS Integration:**
- Fully managed NFS file system for shared storage
- ReadWriteMany access mode for multiple pod access
- Automatic scaling from GB to PB without provisioning
- POSIX-compliant filesystem for git operations and DAG storage
- Regional availability and 99.999999999% (11 9's) durability

**CloudFormation Infrastructure as Code:**
- Complete infrastructure defined in version-controlled templates
- Automated provisioning of VPC, subnets, security groups
- OIDC identity provider for secure service account authentication
- Consistent deployments across environments

## Default Credentials

**AWS RDS Database**: Uses credentials from AWS Secrets Manager
**Airflow Web UI**: `admin/admin123` (created after deployment)
**GitHub Token**: Stored in AWS Secrets Manager at `datasurface/git/credentials`

## Success Criteria

**✅ AWS Infrastructure Deployed:**
- EKS cluster running with Fargate profile
- **Two existing AWS RDS PostgreSQL instances** configured:
  - **Airflow RDS**: Contains airflow_db for Airflow metadata
  - **Merge/Source RDS**: Contains customer_db and merge database for DataSurface operations
- Airflow scheduler and webserver operational on EKS
- Admin user created (admin/admin123)
- AWS Secrets Manager integration configured for existing RDS credentials

**✅ DAGs Deployed:**
- Factory DAGs for dynamic ingestion stream creation
- Infrastructure DAGs for platform management
- All DAGs visible in Airflow UI without parsing errors
- AWS Secrets Manager credentials accessible to DAGs

**✅ Ready for Data Pipeline:**
- **Source database (customer_db)** ready for ingestion on existing Merge/Source RDS instance
- **Merge database** ready for platform operations on existing Merge/Source RDS instance  
- **Airflow database (airflow_db)** operational on existing Airflow RDS instance
- Clean configuration with AWS-native secret management for existing RDS credentials
- IRSA configured for secure AWS service access
- Network connectivity verified between EKS cluster and existing RDS instances

## Network Connectivity Verification and Setup

### Verifying EKS to RDS Connectivity

**CRITICAL**: Before deploying Airflow, verify that the EKS cluster can reach your RDS databases. This is a common issue when using existing RDS instances that may be in different VPCs.

#### Step 1: Check VPC Configuration

```bash
# Get EKS cluster VPC and subnets
export STACK_NAME="your-stack-name"
export EKS_VPC_ID=$(aws eks describe-cluster \
  --name $(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`EKSClusterName`].OutputValue' \
    --output text) \
  --query 'cluster.resourcesVpcConfig.vpcId' \
  --output text \
  --region us-east-1)

echo "EKS Cluster VPC: $EKS_VPC_ID"

# Get RDS instance VPC (replace with your RDS instance identifier)
export RDS_VPC_ID=$(aws rds describe-db-instances \
  --db-instance-identifier aws-postgres-1 \
  --query 'DBInstances[0].DBSubnetGroup.VpcId' \
  --output text \
  --region us-east-1)

echo "RDS Instance VPC: $RDS_VPC_ID"

# Check if they're in the same VPC
if [ "$EKS_VPC_ID" = "$RDS_VPC_ID" ]; then
    echo "✅ EKS and RDS are in the same VPC - no peering needed"
else
    echo "❌ EKS and RDS are in different VPCs - VPC peering required"
    echo "EKS VPC: $EKS_VPC_ID"
    echo "RDS VPC: $RDS_VPC_ID"
fi
```

#### Step 2: Test Database Connectivity from EKS

```bash
# Test basic connectivity to RDS from EKS cluster
kubectl run connectivity-test --rm -i --restart=Never \
  --image=postgres:16 \
  --env="PGPASSWORD=your-db-password" \
  -n ns-yellow-starter \
  -- psql -h your-rds-endpoint.region.rds.amazonaws.com -p 5432 -U postgres -c "SELECT 'Connection Success!' as status, version();"

# If this fails, you need VPC peering (see Step 3)
# If this succeeds, your network connectivity is working
```

#### Step 3: Set Up VPC Peering (If Required)

**When VPC peering is needed:**
- EKS cluster and RDS instance are in different VPCs
- Database connectivity test from Step 2 fails
- Airflow init containers hang indefinitely

**VPC Peering Setup:**

```bash
# 1. Create VPC peering connection
export PEERING_CONNECTION_ID=$(aws ec2 create-vpc-peering-connection \
  --vpc-id $EKS_VPC_ID \
  --peer-vpc-id $RDS_VPC_ID \
  --region us-east-1 \
  --query 'VpcPeeringConnection.VpcPeeringConnectionId' \
  --output text)

echo "Peering Connection ID: $PEERING_CONNECTION_ID"

# 2. Accept the peering connection
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id $PEERING_CONNECTION_ID \
  --region us-east-1

# 3. Wait for peering to become active
aws ec2 wait vpc-peering-connection-exists \
  --vpc-peering-connection-ids $PEERING_CONNECTION_ID \
  --region us-east-1

# 4. Get CIDR blocks for both VPCs
EKS_CIDR=$(aws ec2 describe-vpcs \
  --vpc-ids $EKS_VPC_ID \
  --query 'Vpcs[0].CidrBlock' \
  --output text \
  --region us-east-1)

RDS_CIDR=$(aws ec2 describe-vpcs \
  --vpc-ids $RDS_VPC_ID \
  --query 'Vpcs[0].CidrBlock' \
  --output text \
  --region us-east-1)

echo "EKS VPC CIDR: $EKS_CIDR"
echo "RDS VPC CIDR: $RDS_CIDR"

# 5. Update route tables for EKS VPC (to reach RDS)
EKS_ROUTE_TABLES=$(aws ec2 describe-route-tables \
  --filters "Name=vpc-id,Values=$EKS_VPC_ID" \
  --query 'RouteTables[*].RouteTableId' \
  --output text \
  --region us-east-1)

for rt in $EKS_ROUTE_TABLES; do
  aws ec2 create-route \
    --route-table-id $rt \
    --destination-cidr-block $RDS_CIDR \
    --vpc-peering-connection-id $PEERING_CONNECTION_ID \
    --region us-east-1 || echo "Route may already exist"
done

# 6. Update route tables for RDS VPC (to reach EKS)
RDS_ROUTE_TABLES=$(aws ec2 describe-route-tables \
  --filters "Name=vpc-id,Values=$RDS_VPC_ID" \
  --query 'RouteTables[*].RouteTableId' \
  --output text \
  --region us-east-1)

for rt in $RDS_ROUTE_TABLES; do
  aws ec2 create-route \
    --route-table-id $rt \
    --destination-cidr-block $EKS_CIDR \
    --vpc-peering-connection-id $PEERING_CONNECTION_ID \
    --region us-east-1 || echo "Route may already exist"
done

# 7. Update security groups
# Get RDS security group ID
RDS_SG_ID=$(aws rds describe-db-instances \
  --db-instance-identifier aws-postgres-1 \
  --query 'DBInstances[0].VpcSecurityGroups[0].VpcSecurityGroupId' \
  --output text \
  --region us-east-1)

# Get EKS security group ID
EKS_SG_ID=$(aws eks describe-cluster \
  --name $(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`EKSClusterName`].OutputValue' \
    --output text) \
  --query 'cluster.resourcesVpcConfig.securityGroupIds[0]' \
  --output text \
  --region us-east-1)

# Allow PostgreSQL traffic from EKS to RDS
aws ec2 authorize-security-group-ingress \
  --group-id $RDS_SG_ID \
  --protocol tcp \
  --port 5432 \
  --cidr $EKS_CIDR \
  --region us-east-1 || echo "Rule may already exist"

# Allow outbound PostgreSQL traffic from EKS to RDS
aws ec2 authorize-security-group-egress \
  --group-id $EKS_SG_ID \
  --protocol tcp \
  --port 5432 \
  --cidr $RDS_CIDR \
  --region us-east-1 || echo "Rule may already exist"

echo "✅ VPC peering setup complete"

# 8. Test connectivity after peering
kubectl run peering-test --rm -i --restart=Never \
  --image=postgres:16 \
  --env="PGPASSWORD=your-db-password" \
  -n ns-yellow-starter \
  -- psql -h your-rds-endpoint.region.rds.amazonaws.com -p 5432 -U postgres -c "SELECT 'VPC Peering Success!' as status, version();"
```

#### Step 4: Adding New Data Sources (Production Use Case)

**When adding new RDS instances or data sources in different VPCs:**

```bash
# 1. Identify the new data source VPC
export NEW_SOURCE_VPC_ID=$(aws rds describe-db-instances \
  --db-instance-identifier new-data-source-rds \
  --query 'DBInstances[0].DBSubnetGroup.VpcId' \
  --output text \
  --region us-east-1)

# 2. Check if peering already exists
EXISTING_PEERING=$(aws ec2 describe-vpc-peering-connections \
  --filters "Name=requester-vpc-info.vpc-id,Values=$EKS_VPC_ID" "Name=accepter-vpc-info.vpc-id,Values=$NEW_SOURCE_VPC_ID" \
  --query 'VpcPeeringConnections[0].VpcPeeringConnectionId' \
  --output text \
  --region us-east-1)

if [ "$EXISTING_PEERING" != "None" ] && [ -n "$EXISTING_PEERING" ]; then
    echo "✅ VPC peering already exists: $EXISTING_PEERING"
else
    echo "Creating new VPC peering connection..."
    # Follow the same peering setup steps as above
fi

# 3. Add security group rules for the new data source
NEW_SOURCE_SG_ID=$(aws rds describe-db-instances \
  --db-instance-identifier new-data-source-rds \
  --query 'DBInstances[0].VpcSecurityGroups[0].VpcSecurityGroupId' \
  --output text \
  --region us-east-1)

# Allow access from EKS to new data source
aws ec2 authorize-security-group-ingress \
  --group-id $NEW_SOURCE_SG_ID \
  --protocol tcp \
  --port 5432 \
  --cidr $EKS_CIDR \
  --region us-east-1 || echo "Rule may already exist"

# 4. Test connectivity to new data source
kubectl run new-source-test --rm -i --restart=Never \
  --image=postgres:16 \
  --env="PGPASSWORD=new-source-password" \
  -n ns-yellow-starter \
  -- psql -h new-source-endpoint.region.rds.amazonaws.com -p 5432 -U postgres -c "SELECT 'New Source Connected!' as status;"
```

### Common Network Issues and Solutions

#### Issue: Connectivity Test Hangs or Times Out

**Symptoms:**
- `kubectl run connectivity-test` hangs indefinitely
- Airflow init containers stuck in `Init:0/1` status
- Database connection attempts timeout

**Diagnosis:**
```bash
# Check if VPCs are different
echo "EKS VPC: $EKS_VPC_ID"
echo "RDS VPC: $RDS_VPC_ID"

# Check for existing peering connections
aws ec2 describe-vpc-peering-connections \
  --filters "Name=requester-vpc-info.vpc-id,Values=$EKS_VPC_ID" \
  --query 'VpcPeeringConnections[*].{Status:Status.Code,PeeringId:VpcPeeringConnectionId,AccepterVpc:AccepterVpcInfo.VpcId}' \
  --output table \
  --region us-east-1
```

**Solution:** Follow the VPC peering setup steps above.

#### Issue: Security Group Access Denied

**Symptoms:**
- VPC peering exists but connectivity still fails
- Connection refused errors from database

**Diagnosis:**
```bash
# Check RDS security group rules
aws ec2 describe-security-groups \
  --group-ids $RDS_SG_ID \
  --query 'SecurityGroups[0].IpPermissions[?FromPort==`5432`]' \
  --output table \
  --region us-east-1

# Check if EKS CIDR is allowed
aws ec2 describe-security-groups \
  --group-ids $RDS_SG_ID \
  --query "SecurityGroups[0].IpPermissions[?FromPort==\`5432\` && contains(IpRanges[].CidrIp, '$EKS_CIDR')]" \
  --output table \
  --region us-east-1
```

**Solution:** Add the missing security group rules as shown in Step 3 above.

#### Issue: Route Table Missing Peering Routes

**Symptoms:**
- VPC peering exists but packets don't route correctly
- Intermittent connectivity issues

**Diagnosis:**
```bash
# Check if routes exist in EKS VPC route tables
for rt in $(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$EKS_VPC_ID" --query 'RouteTables[*].RouteTableId' --output text); do
  echo "Route table $rt:"
  aws ec2 describe-route-tables \
    --route-table-ids $rt \
    --query "RouteTables[0].Routes[?DestinationCidrBlock=='$RDS_CIDR']" \
    --output table \
    --region us-east-1
done
```

**Solution:** Add the missing routes as shown in Step 3 above.

### Production Best Practices

#### Automated Connectivity Verification Script

Create a reusable script for verifying connectivity to new data sources:

```bash
cat > verify_data_source_connectivity.sh << 'EOF'
#!/bin/bash

# Usage: ./verify_data_source_connectivity.sh <rds-instance-id> <database-name> <username> <password>
RDS_INSTANCE_ID=$1
DATABASE_NAME=$2
DB_USERNAME=$3
DB_PASSWORD=$4

if [ $# -ne 4 ]; then
    echo "Usage: $0 <rds-instance-id> <database-name> <username> <password>"
    exit 1
fi

echo "=== Verifying connectivity to $RDS_INSTANCE_ID ==="

# Get RDS endpoint and VPC
RDS_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier $RDS_INSTANCE_ID \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

RDS_VPC=$(aws rds describe-db-instances \
  --db-instance-identifier $RDS_INSTANCE_ID \
  --query 'DBInstances[0].DBSubnetGroup.VpcId' \
  --output text)

echo "RDS Endpoint: $RDS_ENDPOINT"
echo "RDS VPC: $RDS_VPC"

# Test connectivity from EKS
kubectl run db-connectivity-check-$(date +%s) --rm -i --restart=Never \
  --image=postgres:16 \
  --env="PGPASSWORD=$DB_PASSWORD" \
  -n ns-yellow-starter \
  -- psql -h $RDS_ENDPOINT -p 5432 -U $DB_USERNAME -d $DATABASE_NAME -c "SELECT 'Success: $RDS_INSTANCE_ID' as status, current_database();"

if [ $? -eq 0 ]; then
    echo "✅ Connectivity verified for $RDS_INSTANCE_ID"
else
    echo "❌ Connectivity failed for $RDS_INSTANCE_ID"
    echo "Check VPC peering and security groups"
fi
EOF

chmod +x verify_data_source_connectivity.sh

# Example usage:
# ./verify_data_source_connectivity.sh aws-postgres-1 airflow_db postgres your-password
```

#### Multi-Source VPC Peering Management

```bash
# List all VPC peering connections for your EKS cluster
aws ec2 describe-vpc-peering-connections \
  --filters "Name=requester-vpc-info.vpc-id,Values=$EKS_VPC_ID" \
  --query 'VpcPeeringConnections[*].{PeeringId:VpcPeeringConnectionId,Status:Status.Code,AccepterVpc:AccepterVpcInfo.VpcId,AccepterCidr:AccepterVpcInfo.CidrBlock}' \
  --output table \
  --region us-east-1

# Check route coverage for all peered VPCs
echo "Checking route coverage..."
for rt in $(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$EKS_VPC_ID" --query 'RouteTables[*].RouteTableId' --output text); do
  echo "Route table $rt routes to peered VPCs:"
  aws ec2 describe-route-tables \
    --route-table-ids $rt \
    --query 'RouteTables[0].Routes[?VpcPeeringConnectionId!=null].{Destination:DestinationCidrBlock,PeeringId:VpcPeeringConnectionId}' \
    --output table \
    --region us-east-1
done
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: PVCs Stuck in Pending State

**Symptoms**: PersistentVolumeClaims remain in `Pending` status, pods cannot start.

**Solution**: Verify EFS CSI driver is properly configured:

```bash
# Check EFS CSI driver status
kubectl get pods -n kube-system -l app=efs-csi-controller

# Verify service account annotation
kubectl describe serviceaccount efs-csi-controller-sa -n kube-system

# Check PVC events for specific errors
kubectl describe pvc <pvc-name> -n <namespace>
```

#### Issue: Pods Cannot Mount EFS Volumes

**Symptoms**: Pods fail to start with volume mount errors.

**Solution**: Ensure EFS security group allows NFS traffic:

```bash
# Get EFS security group ID from CloudFormation
EFS_SG_ID=$(aws cloudformation describe-stacks \
  --stack-name datasurface-eks-stack \
  --query 'Stacks[0].Resources[?LogicalResourceId==`EFSSecurityGroup`].PhysicalResourceId' \
  --output text \
  --region us-east-1)

# Verify NFS rule exists (port 2049)
aws ec2 describe-security-groups --group-ids $EFS_SG_ID --region us-east-1
```

#### Issue: Airflow Pods Crash on Startup

**Symptoms**: Airflow scheduler/webserver pods restart repeatedly.

**Solution**: Check database connectivity and initialization:

```bash
# Check Airflow logs
kubectl logs deployment/airflow-scheduler -n <namespace>

# Test database connection
kubectl run db-test --rm -i --restart=Never \
  --image=postgres:16 \
  --env="PGPASSWORD=<password>" \
  -n <namespace> \
  -- psql -h <db-host> -U <db-user> -c "SELECT version();"
```

#### Issue: AWS Secrets Manager Access Denied

**Symptoms**: Airflow pods crash with secret mounting errors or SQLAlchemy dialect errors:
```
MountVolume.SetUp failed for volume "secrets-store" : rpc error: code = Unknown desc = failed to mount secrets store objects for pod ns-yellow-starter/airflow-scheduler-xxx, err: rpc error: code = Unknown desc = Failed to fetch secret from all regions. Verify secret exists and required permissions are granted for: airflow/connections/postgres_default
```

**Root Cause**: Airflow service account cannot assume its IAM role due to hardcoded OIDC IDs in the CloudFormation template trust policy.

**Solution - Fix OIDC Trust Policy (Same as EFS CSI Driver Issue)**:

This is the same OIDC trust policy issue that affects the EFS CSI driver. The fix was already applied in Stage 2 of the deployment. If you're still getting this error, the trust policy fix may not have been applied correctly.

**Manual verification and fix:**
```bash
# Check if the Airflow role trust policy has the correct OIDC issuer
aws iam get-role --role-name airflow-secrets-role --query 'Role.AssumeRolePolicyDocument'

# If it shows wrong OIDC ID (CE5ACA5A259E350C70EBC961EED62CB2), apply the fix:
# Use the OIDC trust policy fix commands from Stage 2 of the deployment
```

**Common Issues:**
- **Template generates wrong role name**: Generated YAML often contains `airflow-secrets-role` instead of the actual CloudFormation role name
- **CloudFormation role doesn't exist**: If IAM roles stack failed to deploy, the role won't exist despite CloudFormation saying it does
- **Wrong OIDC provider**: Role trust policy references wrong cluster's OIDC provider

**Verification Steps:**
```bash
# Verify IAM role exists and has correct policies
aws iam get-role --role-name <actual-role-name> --region us-east-1
aws iam list-attached-role-policies --role-name <actual-role-name> --region us-east-1
```

#### Issue: EFS CSI Driver Access Denied

**Symptoms**: PVCs stuck in Pending state with "Access Denied" errors in EFS CSI driver logs:
```
failed to provision volume with StorageClass "efs-sc": rpc error: code = Internal desc = Failed to fetch Access Points or Describe File System: operation error STS: AssumeRoleWithWebIdentity, https response error StatusCode: 403, RequestID: xxx, api error AccessDenied: Not authorized to perform sts:AssumeRoleWithWebIdentity
```

**Root Cause**: EFS CSI driver service account lacks proper IAM role trust policy configuration.

**Solution - Manual Fix for OIDC Trust Policy Mismatch**: 

The issue is often caused by hardcoded OIDC IDs in the CloudFormation template that don't match your actual EKS cluster's OIDC provider. Here's how to fix it:

**Step-by-Step Fix:**

```bash
# 1. Get your actual OIDC provider ARN from CloudFormation
export STACK_NAME="your-stack-name"
export OIDC_PROVIDER_ARN=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query "Stacks[0].Outputs[?OutputKey=='EKSOIDCProviderArn'].OutputValue" \
  --output text \
  --region us-east-1)

echo "OIDC Provider ARN: $OIDC_PROVIDER_ARN"

# 2. Extract the OIDC issuer (everything after oidc-provider/)
OIDC_ISSUER=$(echo $OIDC_PROVIDER_ARN | cut -d'/' -f2-)
echo "OIDC Issuer: $OIDC_ISSUER"

# 3. Get the EFS CSI driver role name
export EFS_CSI_DRIVER_ROLE_ARN=$(aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}-iam-roles" \
  --query 'Stacks[0].Outputs[?OutputKey==`EFSCSIDriverRoleArn`].OutputValue' \
  --output text \
  --region us-east-1)

ROLE_NAME=$(echo $EFS_CSI_DRIVER_ROLE_ARN | cut -d'/' -f2)
echo "Role name: $ROLE_NAME"

# 4. Create the correct trust policy
cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "$OIDC_PROVIDER_ARN"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "${OIDC_ISSUER}:sub": "system:serviceaccount:kube-system:efs-csi-controller-sa",
                    "${OIDC_ISSUER}:aud": "sts.amazonaws.com"
                }
            }
        }
    ]
}
EOF

# 5. Update the IAM role trust policy
aws iam update-assume-role-policy \
  --role-name $ROLE_NAME \
  --policy-document file://trust-policy.json \
  --region us-east-1

# 6. Restart the EFS CSI controller
kubectl rollout restart deployment/efs-csi-controller -n kube-system
kubectl rollout status deployment/efs-csi-controller -n kube-system

# 7. Verify PVCs can now bind
kubectl get pvc -n <your-namespace>
```

**Root Cause Explained:**
The CloudFormation template `iam-roles-for-eks.yaml` contains hardcoded OIDC IDs like `CE5ACA5A259E350C70EBC961EED62CB2` in the trust policy conditions for BOTH the EFS CSI driver role AND the Airflow secrets role. Your actual EKS cluster has a different OIDC ID like `00948FA33EBA192925AF570705970A1C`. This mismatch prevents both service accounts from assuming their respective IAM roles.

**Apply the same fix to the Airflow secrets role:**
```bash
# Fix Airflow secrets role trust policy
cat > airflow-trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "$OIDC_PROVIDER_ARN"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "${OIDC_ISSUER}:sub": "system:serviceaccount:ns-yellow-starter:airflow-service-account",
                    "${OIDC_ISSUER}:aud": "sts.amazonaws.com"
                }
            }
        }
    ]
}
EOF

aws iam update-assume-role-policy --role-name airflow-secrets-role --policy-document file://airflow-trust-policy.json
```

**Key Points:**
- Use `StringEquals` (not `StringLike`) for OIDC conditions
- Use the shorter OIDC issuer format (without full ARN prefix in conditions)
- Include both `sub` (subject) and `aud` (audience) conditions
- **IMPORTANT**: The CloudFormation template may have hardcoded OIDC IDs that need manual fixing (see troubleshooting steps above)

**Manual Verification (if needed):**
```bash
# Verify EFS CSI driver service account annotation
kubectl describe serviceaccount efs-csi-controller-sa -n kube-system

# Test role assumption
kubectl run test-efs-permissions --rm -i --restart=Never \
  --image=amazon/aws-cli:latest \
  --serviceaccount=efs-csi-controller-sa \
  -n kube-system \
  -- aws sts get-caller-identity

# Check PVC status after fix
kubectl get pvc -n <namespace>
```


#### Issue: Pods Stuck in Pending - Insufficient CPU

**Symptoms**: Airflow scheduler shows "Insufficient cpu" and remains in `Pending` status.

**Cause**: Default Airflow resource requests (scheduler: 2 CPU, webserver: 1 CPU) exceed capacity of `m5.large` nodes (2 vCPU each).

**Solutions**:

**Option A: Use Larger Instance Types (Recommended)**
```bash
# Update CloudFormation to use m5.xlarge or larger
aws cloudformation update-stack \
  --stack-name datasurface-eks-v3 \
  --template-body file://aws-marketplace/cloudformation/datasurface-eks-stack.yaml \
  --parameters ParameterKey=InstanceType,ParameterValue=m5.xlarge \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

**Option B: Temporarily Patch Resource Requests**
```bash
# Reduce scheduler CPU request
kubectl patch deployment airflow-scheduler -n ns-yellow-starter -p '{"spec":{"template":{"spec":{"containers":[{"name":"airflow","resources":{"requests":{"cpu":"500m","memory":"1Gi"}}}]}}}}'

# Reduce webserver CPU request  
kubectl patch deployment airflow-webserver -n ns-yellow-starter -p '{"spec":{"template":{"spec":{"containers":[{"name":"airflow","resources":{"requests":{"cpu":"500m","memory":"1Gi"}}}]}}}}'
```

**Instance Type Recommendations**:
- `m5.large` (2 vCPU): Only suitable with reduced resource requests
- `m5.xlarge` (4 vCPU): Recommended minimum for default resource requests
- `m5.2xlarge` (8 vCPU): Good for production workloads
- `m5.4xlarge` (16 vCPU): Excellent for heavy workloads or multiple environments

### Performance Optimization

#### EFS Performance Mode

For high-throughput workloads, consider using EFS Max I/O mode:

```bash
# Check current EFS performance mode
aws efs describe-file-systems --file-system-id <efs-id> --region us-east-1
```

#### Node Group Scaling

Adjust node group size based on workload requirements:

```bash
# Update node group scaling configuration
aws eks update-nodegroup-config \
  --cluster-name <cluster-name> \
pwd  --nodegroup-name <nodegroup-name> \
  --scaling-config minSize=1,maxSize=10,desiredSize=3 \
  --region us-east-1
```

## Known Issues and Manual Fixes Required

**⚠️ CRITICAL**: The following issues require manual intervention after artifact generation. These represent gaps between the template generation and CloudFormation reality that need to be addressed.

### Issue 1: IAM Role ARN Mismatch (BLOCKING)

**Symptoms**: Airflow init containers hang indefinitely with no logs, eventually get OOMKilled.

**Root Cause**: Template generates hardcoded role ARN that doesn't match CloudFormation's auto-generated role names.

**Template Generates**: `arn:aws:iam::479984738272:role/airflow-secrets-role`
**CloudFormation Creates**: `arn:aws:iam::479984738272:role/ds-eks-m5-v5-iam-roles-AirflowSecretsRole-6PRSTdC9kgcr`

**Manual Fix Required After Artifact Generation**:
```bash
# 1. Get the actual role ARN from CloudFormation
export AIRFLOW_ROLE_ARN=$(aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}-iam-roles" \
  --query 'Stacks[0].Outputs[?OutputKey==`AirflowSecretsRoleArn`].OutputValue' \
  --output text \
  --region us-east-1)

echo "Actual Role ARN: $AIRFLOW_ROLE_ARN"

# 2. Update the generated YAML file
sed -i "s|arn:aws:iam::479984738272:role/airflow-secrets-role|$AIRFLOW_ROLE_ARN|g" \
  generated_output/Test_DP/kubernetes-bootstrap.yaml

# 3. Verify the fix
grep "role-arn" generated_output/Test_DP/kubernetes-bootstrap.yaml
```

### Issue 2: AWS Secrets Manager Backend Timeout

**Symptoms**: `airflow db init` command hangs when using `sql_alchemy_conn_cmd` approach.

**Root Cause**: Airflow's SecretsManagerBackend times out during database initialization, even with correct IAM permissions.

**Diagnostic Commands**:
```bash
# Test AWS connectivity from init container
kubectl exec <scheduler-pod> -n ns-yellow-starter -c airflow-db-init -- \
  timeout 5 python -c "import boto3; print(boto3.client('sts').get_caller_identity())"

# Test SecretsManagerBackend (this will timeout)
kubectl exec <scheduler-pod> -n ns-yellow-starter -c airflow-db-init -- \
  timeout 10 python -c "
from airflow.providers.amazon.aws.secrets.secrets_manager import SecretsManagerBackend
backend = SecretsManagerBackend(connections_prefix='airflow/connections')
conn = backend.get_connection('postgres_default')
print(conn.get_uri())
"
```

**Current Workaround**: Use hardcoded database connection in init container environment variable.

### Issue 3: Template Database Configuration

**Problem**: The `psp_airflow.yaml.j2` template has an empty `{{ airflow_db_url }}` variable, causing SQLite fallback.

**Template Fix Applied**:
```yaml
[database]
sql_alchemy_conn_cmd = python -c "import os; from airflow.providers.amazon.aws.secrets.secrets_manager import SecretsManagerBackend; backend = SecretsManagerBackend(connections_prefix='airflow/connections'); conn = backend.get_connection('postgres_default'); print(conn.get_uri())"
```

**Issue**: This approach causes init container timeouts.

### Issue 4: Init Container Resource Limits

**Symptoms**: Multiple `Init:OOMKilled` events despite node capacity availability.

**Cause**: Init containers have no resource limits specified, hitting default namespace limits.

**Manual Fix**: Add resource limits to init containers in generated YAML:
```yaml
initContainers:
- name: airflow-db-init
  # ... existing config ...
  resources:
    requests:
      memory: 2Gi
      cpu: 500m
    limits:
      memory: 4Gi
      cpu: 1000m
```

### Issue 5: AWS Secrets Manager Secret Format (RESOLVED)

**Hybrid Approach - Correct Formats:**

**Static Secrets (CSI Driver - File-based)**:
```bash
# Airflow database connection (mounted as file)
Secret: airflow/connections/postgres_default
Format: PostgreSQL URI string
Content: postgresql://postgres:password@host:port/database
```

**Dynamic Secrets (boto3 API - Runtime)**:
```json
# DataSurface job credentials (API access)
{
  "postgres_USER": "postgres",
  "postgres_PASSWORD": "password"
}
```

**Key Point**: The secret format must match the access method - URI strings for file-based reading, JSON objects for API-based access.

### Recommended Next Steps for Tomorrow

1. **Fix CloudFormation Template**: Add `RoleName: airflow-secrets-role` to create predictable role names
2. **Fix OIDC Trust Policy Template**: Update `iam-roles-for-eks.yaml` to dynamically extract OIDC issuer from parameter instead of hardcoding OIDC IDs
3. **Update Template Variables**: Make the AWS assembly provide the correct role ARN pattern
4. **Template Automation**: Create post-deployment script to automatically update role ARNs and trust policies

### Working Components (Don't Change)

- ✅ **Two-stage CloudFormation deployment** - EKS cluster + IAM roles separation works
- ✅ **EFS CSI driver configuration** - Trust policy format and annotation process works
- ✅ **Docker multiplatform builds** - Both datasurface/datasurface:latest and datasurface/airflow:2.11.0-aws work
- ✅ **AWS Secrets Manager access** - IAM roles and IRSA work correctly when role ARN is correct
- ✅ **EFS storage class and PVC binding** - EFS integration works properly (see troubleshooting for OIDC trust policy fix if needed)

