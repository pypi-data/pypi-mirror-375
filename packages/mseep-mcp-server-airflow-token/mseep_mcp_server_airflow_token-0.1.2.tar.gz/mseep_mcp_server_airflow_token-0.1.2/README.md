# mcp-server-airflow-token

A Model Context Protocol (MCP) server for Apache Airflow with Bearer token authentication support, enabling seamless integration with Astronomer Cloud and standalone Airflow instances.

> **Based on [mcp-server-apache-airflow](https://github.com/yangkyeongmo/mcp-server-apache-airflow) by Gyeongmo Nathan Yang**
> 
> This fork enhances the original MCP server with **Bearer token authentication support**, making it compatible with Astronomer Cloud and other token-based Airflow deployments.

## Key Enhancements

- ✅ **Bearer Token Authentication** - Primary authentication method for modern Airflow deployments
- ✅ **Astronomer Cloud Compatible** - Works seamlessly with Astronomer's managed Airflow
- ✅ **Backward Compatible** - Still supports username/password authentication
- ✅ **Enhanced URL Handling** - Correctly handles deployment paths like `/deployment-id`

## About

This project implements a [Model Context Protocol](https://modelcontextprotocol.io/introduction) server that wraps Apache Airflow's REST API, allowing MCP clients to interact with Airflow in a standardized way. It uses the official Apache Airflow client library to ensure compatibility and maintainability.

## Feature Implementation Status

| Feature                          | API Path                                                                                      | Status |
| -------------------------------- | --------------------------------------------------------------------------------------------- | ------ |
| **DAG Management**         |                                                                                               |        |
| List DAGs                        | `/api/v1/dags`                                                                              | ✅     |
| Get DAG Details                  | `/api/v1/dags/{dag_id}`                                                                     | ✅     |
| Pause DAG                        | `/api/v1/dags/{dag_id}`                                                                     | ✅     |
| Unpause DAG                      | `/api/v1/dags/{dag_id}`                                                                     | ✅     |
| Update DAG                       | `/api/v1/dags/{dag_id}`                                                                     | ✅     |
| Delete DAG                       | `/api/v1/dags/{dag_id}`                                                                     | ✅     |
| Get DAG Source                   | `/api/v1/dagSources/{file_token}`                                                           | ✅     |
| Patch Multiple DAGs              | `/api/v1/dags`                                                                              | ✅     |
| Reparse DAG File                 | `/api/v1/dagSources/{file_token}/reparse`                                                   | ✅     |
| **DAG Runs**               |                                                                                               |        |
| List DAG Runs                    | `/api/v1/dags/{dag_id}/dagRuns`                                                             | ✅     |
| Create DAG Run                   | `/api/v1/dags/{dag_id}/dagRuns`                                                             | ✅     |
| Get DAG Run Details              | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}`                                                | ✅     |
| Update DAG Run                   | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}`                                                | ✅     |
| Delete DAG Run                   | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}`                                                | ✅     |
| Get DAG Runs Batch               | `/api/v1/dags/~/dagRuns/list`                                                               | ✅     |
| Clear DAG Run                    | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/clear`                                          | ✅     |
| Set DAG Run Note                 | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/setNote`                                        | ✅     |
| Get Upstream Dataset Events      | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/upstreamDatasetEvents`                          | ✅     |
| **Tasks**                  |                                                                                               |        |
| List DAG Tasks                   | `/api/v1/dags/{dag_id}/tasks`                                                               | ✅     |
| Get Task Details                 | `/api/v1/dags/{dag_id}/tasks/{task_id}`                                                     | ✅     |
| Get Task Instance                | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}`                        | ✅     |
| List Task Instances              | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances`                                  | ✅     |
| Update Task Instance             | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}`                        | ✅     |
| Clear Task Instances             | `/api/v1/dags/{dag_id}/clearTaskInstances`                                                  | ✅     |
| Set Task Instances State         | `/api/v1/dags/{dag_id}/updateTaskInstancesState`                                            | ✅     |
| **Variables**              |                                                                                               |        |
| List Variables                   | `/api/v1/variables`                                                                         | ✅     |
| Create Variable                  | `/api/v1/variables`                                                                         | ✅     |
| Get Variable                     | `/api/v1/variables/{variable_key}`                                                          | ✅     |
| Update Variable                  | `/api/v1/variables/{variable_key}`                                                          | ✅     |
| Delete Variable                  | `/api/v1/variables/{variable_key}`                                                          | ✅     |
| **Connections**            |                                                                                               |        |
| List Connections                 | `/api/v1/connections`                                                                       | ✅     |
| Create Connection                | `/api/v1/connections`                                                                       | ✅     |
| Get Connection                   | `/api/v1/connections/{connection_id}`                                                       | ✅     |
| Update Connection                | `/api/v1/connections/{connection_id}`                                                       | ✅     |
| Delete Connection                | `/api/v1/connections/{connection_id}`                                                       | ✅     |
| Test Connection                  | `/api/v1/connections/test`                                                                  | ✅     |
| **Pools**                  |                                                                                               |        |
| List Pools                       | `/api/v1/pools`                                                                             | ✅     |
| Create Pool                      | `/api/v1/pools`                                                                             | ✅     |
| Get Pool                         | `/api/v1/pools/{pool_name}`                                                                 | ✅     |
| Update Pool                      | `/api/v1/pools/{pool_name}`                                                                 | ✅     |
| Delete Pool                      | `/api/v1/pools/{pool_name}`                                                                 | ✅     |
| **XComs**                  |                                                                                               |        |
| List XComs                       | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/xcomEntries`            | ✅     |
| Get XCom Entry                   | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/xcomEntries/{xcom_key}` | ✅     |
| **Datasets**               |                                                                                               |        |
| List Datasets                    | `/api/v1/datasets`                                                                          | ✅     |
| Get Dataset                      | `/api/v1/datasets/{uri}`                                                                    | ✅     |
| Get Dataset Events               | `/api/v1/datasetEvents`                                                                     | ✅     |
| Create Dataset Event             | `/api/v1/datasetEvents`                                                                     | ✅     |
| Get DAG Dataset Queued Event     | `/api/v1/dags/{dag_id}/dagRuns/queued/datasetEvents/{uri}`                                  | ✅     |
| Get DAG Dataset Queued Events    | `/api/v1/dags/{dag_id}/dagRuns/queued/datasetEvents`                                        | ✅     |
| Delete DAG Dataset Queued Event  | `/api/v1/dags/{dag_id}/dagRuns/queued/datasetEvents/{uri}`                                  | ✅     |
| Delete DAG Dataset Queued Events | `/api/v1/dags/{dag_id}/dagRuns/queued/datasetEvents`                                        | ✅     |
| Get Dataset Queued Events        | `/api/v1/datasets/{uri}/dagRuns/queued/datasetEvents`                                       | ✅     |
| Delete Dataset Queued Events     | `/api/v1/datasets/{uri}/dagRuns/queued/datasetEvents`                                       | ✅     |
| **Monitoring**             |                                                                                               |        |
| Get Health                       | `/api/v1/health`                                                                            | ✅     |
| **DAG Stats**              |                                                                                               |        |
| Get DAG Stats                    | `/api/v1/dags/statistics`                                                                   | ✅     |
| **Config**                 |                                                                                               |        |
| Get Config                       | `/api/v1/config`                                                                            | ✅     |
| **Plugins**                |                                                                                               |        |
| Get Plugins                      | `/api/v1/plugins`                                                                           | ✅     |
| **Providers**              |                                                                                               |        |
| List Providers                   | `/api/v1/providers`                                                                         | ✅     |
| **Event Logs**             |                                                                                               |        |
| List Event Logs                  | `/api/v1/eventLogs`                                                                         | ✅     |
| Get Event Log                    | `/api/v1/eventLogs/{event_log_id}`                                                          | ✅     |
| **System**                 |                                                                                               |        |
| Get Import Errors                | `/api/v1/importErrors`                                                                      | ✅     |
| Get Import Error Details         | `/api/v1/importErrors/{import_error_id}`                                                    | ✅     |
| Get Health Status                | `/api/v1/health`                                                                            | ✅     |
| Get Version                      | `/api/v1/version`                                                                           | ✅     |

## Setup

### Dependencies

This project depends on the official Apache Airflow client library (`apache-airflow-client`). It will be automatically installed when you install this package.

### Environment Variables

Set the following environment variables:

#### Token Authentication (Recommended)
```
AIRFLOW_HOST=<your-airflow-host>        # Optional, defaults to http://localhost:8080
AIRFLOW_TOKEN=<your-airflow-api-token>  # Your Airflow API token
AIRFLOW_API_VERSION=v1                  # Optional, defaults to v1
```

#### Basic Authentication (Alternative)
```
AIRFLOW_HOST=<your-airflow-host>        # Optional, defaults to http://localhost:8080
AIRFLOW_USERNAME=<your-airflow-username>
AIRFLOW_PASSWORD=<your-airflow-password>
AIRFLOW_API_VERSION=v1                  # Optional, defaults to v1
```

Note: If `AIRFLOW_TOKEN` is provided, it will be used for authentication. Otherwise, the server will fall back to basic authentication using username and password.

### Usage with Claude Desktop

First, clone the repository:
```bash
git clone https://github.com/nikhil-ganage/mcp-server-airflow-token
```

Add to your `claude_desktop_config.json`:

#### With Token Authentication (Recommended)
```json
{
  "mcpServers": {
    "apache-airflow": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "path-to-repo/mcp-server-airflow-token",
        "run",
        "mcp-server-airflow-token"
      ],
      "env": {
        "AIRFLOW_HOST": "https://astro_id.astronomer.run/id",
        "AIRFLOW_TOKEN": "TOKEN"
      }
    }
  }
}
```

#### With Basic Authentication
```json
{
  "mcpServers": {
    "mcp-server-airflow-token": {
      "command": "uvx",
      "args": ["mcp-server-airflow-token"],
      "env": {
        "AIRFLOW_HOST": "https://your-airflow-host",
        "AIRFLOW_USERNAME": "your-username",
        "AIRFLOW_PASSWORD": "your-password"
      }
    }
  }
}
```

For read-only mode (recommended for safety):

#### Read-only with Token Authentication
```json
{
  "mcpServers": {
    "mcp-server-airflow-token": {
      "command": "uvx",
      "args": ["mcp-server-airflow-token", "--read-only"],
      "env": {
        "AIRFLOW_HOST": "https://your-airflow-host",
        "AIRFLOW_TOKEN": "your-api-token"
      }
    }
  }
}
```

#### Read-only with Basic Authentication
```json
{
  "mcpServers": {
    "mcp-server-airflow-token": {
      "command": "uvx",
      "args": ["mcp-server-airflow-token", "--read-only"],
      "env": {
        "AIRFLOW_HOST": "https://your-airflow-host",
        "AIRFLOW_USERNAME": "your-username",
        "AIRFLOW_PASSWORD": "your-password"
      }
    }
  }
}
```

Replace `path-to-repo` with the actual path where you've cloned the repository.

### Astronomer Cloud Configuration Example

For Astronomer Cloud deployments:

```json
{
  "mcpServers": {
    "mcp-server-airflow-token": {
      "command": "uvx",
      "args": ["mcp-server-airflow-token"],
      "env": {
        "AIRFLOW_HOST": "https://your-astronomer-domain.astronomer.run/your-deployment-id",
        "AIRFLOW_TOKEN": "your-astronomer-api-token"
      }
    }
  }
}
```

Note: The deployment ID is part of your Astronomer Cloud URL path.

### Selecting the API groups

You can select the API groups you want to use by setting the `--apis` flag.

```bash
uv run mcp-server-airflow-token --apis "dag,dagrun"
```

The default is to use all APIs.

Allowed values are:

- config
- connections
- dag
- dagrun
- dagstats
- dataset
- eventlog
- importerror
- monitoring
- plugin
- pool
- provider
- taskinstance
- variable
- xcom

### Read-Only Mode

You can run the server in read-only mode by using the `--read-only` flag. This will only expose tools that perform read operations (GET requests) and exclude any tools that create, update, or delete resources.

```bash
uv run mcp-server-airflow-token --read-only
```

In read-only mode, the server will only expose tools like:
- Listing DAGs, DAG runs, tasks, variables, connections, etc.
- Getting details of specific resources
- Reading configurations and monitoring information
- Testing connections (non-destructive)

Write operations like creating, updating, deleting DAGs, variables, connections, triggering DAG runs, etc. will not be available in read-only mode.

You can combine read-only mode with API group selection:

```bash
uv run mcp-server-airflow-token --read-only --apis "dag,variable"
```

### Manual Execution

You can also run the server manually:

```bash
make run
```

`make run` accepts following options:

Options:

- `--port`: Port to listen on for SSE (default: 8000)
- `--transport`: Transport type (stdio/sse, default: stdio)

Or, you could run the sse server directly, which accepts same parameters:

```bash
make run-sse
```

### Installation

You can install the server using pip or uvx:

```bash
# Using pip
pip install mcp-server-airflow-token

# Using uvx (recommended)
uvx mcp-server-airflow-token
```

## Development

### Setting up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/nikhil-ganage/mcp-server-airflow-token.git
cd mcp-server-airflow-token
```

2. Install development dependencies:
```bash
uv sync --dev
```

3. Create a `.env` file for environment variables (optional for development):
```bash
touch .env
```

> **Note**: No environment variables are required for running tests. The `AIRFLOW_HOST` defaults to `http://localhost:8080` for development and testing purposes.

### Running Tests

The project uses pytest for testing with the following commands available:

```bash
# Run all tests
make test
```

### Code Quality

```bash
# Run linting
make lint

# Run code formatting
make format
```

### Continuous Integration

The project includes a GitHub Actions workflow (`.github/workflows/test.yml`) that automatically:

- Runs tests on Python 3.10, 3.11, and 3.12
- Executes linting checks using ruff
- Runs on every push and pull request to `main` branch

The CI pipeline ensures code quality and compatibility across supported Python versions before any changes are merged.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

The package is deployed automatically to PyPI when project.version is updated in `pyproject.toml`.
Follow semver for versioning.

Please include version update in the PR in order to apply the changes to core logic.

## License

[MIT License](LICENSE)
