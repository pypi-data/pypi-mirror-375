# Chaos Mesh MCP Server

An MCP server that enables AI agents to perform chaos engineering through Chaos Mesh on EKS clusters.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Agent      │───▶│   MCP Server     │───▶│  EKS Cluster    │
│                 │    │                  │    │                 │
│ - Failure       │    │ - OIDC Auth      │    │ - Chaos Mesh    │
│   Scenarios     │    │ - K8s API Calls  │    │ - Workloads     │
│ - Experiment    │    │ - Experiment     │    │ - Monitoring    │
│   Planning      │    │   Management     │    │ - Resource Info │
│ - Result        │    │ - Resource Query │    │                 │
│   Analysis      │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Key Features

### 1. Authentication and Authorization Management

- OIDC-based EKS cluster authentication
- RBAC permission validation
- Token renewal and management

### 2. Chaos Mesh Experiment Management

- Experiment creation and execution
- Experiment status monitoring
- Experiment termination and cleanup

### 3. Chaos Engineering Tools

- Pod failure injection
- Network failure simulation
- Storage failure testing
- Time and stress testing

### 4. EKS Cluster Resource Management

- Node information retrieval
- Namespace listing and details
- Deployment status monitoring
- Service discovery
- Pod status and health checks
- Cluster summary information

## Available MCP Tools

### Cluster Management
- `add_remote_cluster` - Add EKS cluster to management
- `list_remote_clusters` - List all managed clusters
- `install_chaos_mesh` - Install Chaos Mesh on cluster

### Resource Information
- `get_cluster_nodes` - Get detailed node information
- `get_cluster_namespaces` - Get namespace information
- `get_cluster_deployments` - Get deployment status (all or specific namespace)
- `get_cluster_services` - Get service information (all or specific namespace)
- `get_cluster_pods` - Get pod information (all or specific namespace)
- `get_cluster_resource_summary` - Get cluster resource overview and summary

### Chaos Experiments
- `create_pod_chaos_experiment` - Create pod failure experiments
- `create_network_chaos_experiment` - Create network failure experiments
- `create_stress_chaos_experiment` - Create stress testing experiments
- `create_io_chaos_experiment` - Create I/O failure experiments
- `create_dns_chaos_experiment` - Create DNS failure experiments
- `create_time_chaos_experiment` - Create time manipulation experiments

## Installation and Setup

1. Install Chaos Mesh on EKS cluster
2. Configure OIDC provider
3. Set up RBAC permissions
4. Deploy MCP server

## Security Considerations

- Apply principle of least privilege
- Limit experiment scope
- Record audit logs
- Implement safety mechanisms

## Usage

> Before setting the cluster, you should add IAM Role to cluster RBAC group to access your cluster with system:managers permission.
> You can add it with [Kubernets RBAC configuration](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
> You also add a mapping between an IAM role to a Kubernetes user and groups.
> With AWS CDK, see [Masters Role](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_eks-readme.html#masters-role) and [addRoleMapping](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_eks.AwsAuth.html#addwbrrolewbrmappingrole-mapping)

You can initialize your cluster with env or manually add with add_remote_cluter tool.

### \*.json file

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "uvx",
      "args": ["chaos-mesh-mcp-server@latest"],
      "env": {
        "CLUSTERS_CONFIG": "{my-cluster-name}:{my-cluster-region},{my-cluster-2-name}:{my-cluster-2-region}"
        "AWS_ACCESS_KEY": "KEY",
        "AWS_SECRET_ID": "SECRET",
      }
    }
  }
}
```

### Strands Agent SDK

```python
chaos_mesh_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["chaos-mesh-mcp-server@latest"],
            env={
                "CLUSTERS_CONFIG": "{my-cluster-name}:{my-cluster-region},{my-cluster-2-name}:{my-cluster-2-region}",
                "AWS_ACCESS_KEY": "KEY",
                "AWS_SECRET_ID": "SECRET",
            },
        )
    )
)

chaos_mesh_mcp_client.start()

agent = Agent(
    model,
    system_prompt,
    tools=[chaos_mesh_mcp_client.list_tools_sync()],
)
```

## Example Usage

### Get Cluster Information
```python
# Get cluster summary
cluster_summary = await get_cluster_resource_summary("my-cluster")

# Get specific resource information
nodes = await get_cluster_nodes("my-cluster")
namespaces = await get_cluster_namespaces("my-cluster")
deployments = await get_cluster_deployments("my-cluster", "default")
```

### Create Chaos Experiments
```python
# Create pod chaos experiment
result = await create_pod_chaos_experiment(
    cluster_name="my-cluster",
    namespace="default",
    target_app="my-app",
    action="pod-kill",
    duration="30s"
)
```
