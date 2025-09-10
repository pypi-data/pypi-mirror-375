# 🤖 MCP Selenium Grid

[![Tests](https://github.com/CatchNip/mcp-selenium-grid/actions/workflows/1_tests.yml/badge.svg?branch=main)](https://github.com/CatchNip/mcp-selenium-grid/actions/workflows/1_tests.yml)
![GitHub Last Commit](https://img.shields.io/github/last-commit/CatchNip/mcp-selenium-grid)
[![GitHub Release](https://img.shields.io/github/v/release/CatchNip/mcp-selenium-grid?include_prereleases)](https://github.com/CatchNip/mcp-selenium-grid/releases)
![GitHub commits since latest release](https://img.shields.io/github/commits-since/CatchNip/mcp-selenium-grid/latest?include_prereleases)
![GitHub Commit Activity](https://img.shields.io/github/commit-activity/m/CatchNip/mcp-selenium-grid)
![GitHub Contributors](https://img.shields.io/github/contributors/CatchNip/mcp-selenium-grid?label=Contributors)
[![License](https://img.shields.io/github/license/CatchNip/mcp-selenium-grid)](LICENSE)

A Model Context Protocol (MCP) server for managing Selenium Grid browser instances. Useful for browser automation and testing workflows.

The MCP Selenium Grid provides a MCP Server for creating and managing browser instances in both Docker and Kubernetes environments. It's designed to work with AI agents and automation tools that need browser automation capabilities.

## Key Features

- **Multi-browser support**: Chrome, Firefox and Edge
- **Dual backend support**: Docker and Kubernetes deployment modes
- **Secure API**: Token-based authentication for browser management
- **Scalable architecture**: Support for multiple browser instances
- **MCP compliance**: Follows Model Context Protocol standards

## 🚀 Quick Start

### Prerequisites

- [uv](https://github.com/astral-sh/uv) (Python dependency manager)
- [Docker](https://www.docker.com/) (for Docker deployment mode)
- [K3s](https://k3s.io/) (for Kubernetes deployment mode, optional)

### 📖 Usage

The MCP Selenium Grid provides a Web API for creating and managing browser instances. The server runs on `localhost:8000` and exposes MCP endpoints at `/mcp` (Http Transport) and `/sse` (Server Sent Events).
> Note: All requests to the server root `http://localhost:8000` will be redirected to either `/mcp` or `/sse` endpoints, depending on the request, but you can choose to use directly `/mcp` (Http Transport) or `/sse` (Server Sent Events) endpoints.

### Known Issues & Limitations

- When you use [STDIO transport](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#stdio) with the `--stdio` flag, the MCP Servers do not shut down the same way they do in the terminal. To clean up resources and remove containers or pods, run:

    ```bash
    uv run mcp-selenium-grid clean
    ```

    ```bash
    uv run mcp-selenium-grid clean -d kubernetes
    ```

### MCP Client Configuration

#### 🐳 Docker Deployment

For Docker-based deployment, ensure Docker is running and use the Docker configuration in your MCP client setup.

```json
{
  "mcpServers": {
    "mcp-selenium-grid": {
      "command": "uvx",
      "args": ["mcp-selenium-grid", "server", "run",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--stdio",
      ],
      "env": {
        "AUTH_ENABLED": "false",
        "ALLOWED_ORIGINS": "[\"http://127.0.0.1:8000\"]",
        "DEPLOYMENT_MODE": "docker",
        "SELENIUM_GRID__USERNAME": "USER",
        "SELENIUM_GRID__PASSWORD": "CHANGE_ME",
        "SELENIUM_GRID__VNC_PASSWORD": "CHANGE_ME",
        "SELENIUM_GRID__VNC_VIEW_ONLY": "false",
        "SELENIUM_GRID__MAX_BROWSER_INSTANCES": "4",
        "SELENIUM_GRID__SE_NODE_MAX_SESSIONS": "1",
        "FASTMCP_EXPERIMENTAL_ENABLE_NEW_OPENAPI_PARSER": "true"
      }
    }
  }
}
```

> The server will be available at `http://localhost:8000` with interactive API documentation at `http://localhost:8000/docs`.

#### ☸️ Kubernetes Deployment

##### 3. Kubernetes Setup (Optional)

This project supports Kubernetes deployment for scalable browser instance management. We use K3s for local development and testing.

###### Install K3s (<https://docs.k3s.io/quick-start>)

```bash
# Install K3s
curl -sfL https://get.k3s.io | sh -

# Verify installation
k3s --version

# Start if not running
sudo systemctl start k3s
```

###### Create K3s Kubernetes Context

After installing K3s, you might want to create a dedicated `kubectl` context for it:

```bash
# Copy K3s kubeconfig
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config-local-k3s
sudo chown $USER:$USER ~/.kube/config-local-k3s
chmod 600 ~/.kube/config-local-k3s

# Create context
KUBECONFIG=~/.kube/config-local-k3s \
kubectl config set-context k3s-selenium-grid \
  --cluster=default \
  --user=default
```

###### Deploy Selenium Grid

Please run for help to get to know the available commands and parameters:

```bash
uvx mcp-selenium-grid helm --help
uvx mcp-selenium-grid helm deploy --help
uvx mcp-selenium-grid helm uninstall --help
```

Deploy using default parameters:

```bash
uvx mcp-selenium-grid helm deploy
```

Uninstall using default parameters:

```bash
# using default parameters
uvx mcp-selenium-grid helm uninstall --delete-namespace
```

```json
{
  "mcpServers": {
    "mcp-selenium-grid": {
      "command": "uvx",
      "args": ["mcp-selenium-grid", "server", "run",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--stdio",
      ],
      "env": {
        "AUTH_ENABLED": "false",
        "ALLOWED_ORIGINS": "[\"http://127.0.0.1:8000\"]",
        "DEPLOYMENT_MODE": "kubernetes",
        "SELENIUM_GRID__USERNAME": "USER",
        "SELENIUM_GRID__PASSWORD": "CHANGE_ME",
        "SELENIUM_GRID__VNC_PASSWORD": "CHANGE_ME",
        "SELENIUM_GRID__VNC_VIEW_ONLY": "false",
        "SELENIUM_GRID__MAX_BROWSER_INSTANCES": "4",
        "SELENIUM_GRID__SE_NODE_MAX_SESSIONS": "1",
        "KUBERNETES__KUBECONFIG": "~/.kube/config-local-k3s",
        "KUBERNETES__CONTEXT": "k3s-selenium-grid",
        "KUBERNETES__NAMESPACE": "selenium-grid-dev",
        "KUBERNETES__SELENIUM_GRID_SERVICE_NAME": "selenium-grid",
        "FASTMCP_EXPERIMENTAL_ENABLE_NEW_OPENAPI_PARSER": "true"
      }
    }
  }
}
```

```json
{
  "mcpServers": {
    "mcp-selenium-grid": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--init",
        "--network=host",
        "-v", "/home/user/.kube/config-local-k3s:/.kube/config-local-k3s:ro", // path to your kubeconfig file
        "-e", "AUTH_ENABLED=false",
        "-e", "ALLOWED_ORIGINS=[\\\"http://127.0.0.1:8000\\\"]",
        "-e", "DEPLOYMENT_MODE=kubernetes", // required for docker
        "-e", "SELENIUM_GRID__USERNAME=USER",
        "-e", "SELENIUM_GRID__PASSWORD=CHANGE_ME",
        "-e", "SELENIUM_GRID__VNC_PASSWORD=CHANGE_ME",
        "-e", "SELENIUM_GRID__VNC_VIEW_ONLY=false",
        "-e", "SELENIUM_GRID__MAX_BROWSER_INSTANCES=4",
        "-e", "SELENIUM_GRID__SE_NODE_MAX_SESSIONS=1",
        "-e", "KUBERNETES__KUBECONFIG=/.kube/config-local-k3s", // path to your kubeconfig file
        "-e", "KUBERNETES__USE_HOST_DOCKER_INTERNAL=true",
        "-e", "KUBERNETES__CONTEXT=k3s-selenium-grid",
        "-e", "KUBERNETES__NAMESPACE=selenium-grid-dev",
        "-e", "KUBERNETES__SELENIUM_GRID_SERVICE_NAME=selenium-grid",
        "-e", "FASTMCP_EXPERIMENTAL_ENABLE_NEW_OPENAPI_PARSER=true",
        "ghcr.io/catchnip/mcp-selenium-grid:latest"
      ]
    }
  }
}

```

> The server will be available at `http://localhost:8000` with interactive API documentation at `http://localhost:8000/docs`.

### Server with auth enabled

#### UVX

Using default args

```bash
uvx mcp-selenium-grid server run
```

Custom args

```bash
API_TOKEN=CHANGE_ME uvx mcp-selenium-grid server run --host 127.0.0.1 --port 8000
```

#### Docker

Default args

```bash
docker run -i --rm --init --network=host \
  -v ~/.kube/config-local-k3s:/kube/config-local-k3s:ro \
  -e KUBERNETES__KUBECONFIG=/kube/config-local-k3s \
  ghcr.io/catchnip/mcp-selenium-grid:latest
```

Custom args

```bash
docker run -i --rm --init \
  --network=host \
  -v ~/.kube/config-local-k3s:/kube/config-local-k3s:ro \
  -e API_TOKEN=CHANGE_ME \
  -e ALLOWED_ORIGINS='["http://127.0.0.1:8000"]' \
  -e DEPLOYMENT_MODE=kubernetes \
  -e SELENIUM_GRID__USERNAME=USER \
  -e SELENIUM_GRID__PASSWORD=CHANGE_ME \
  -e SELENIUM_GRID__VNC_PASSWORD=CHANGE_ME \
  -e SELENIUM_GRID__VNC_VIEW_ONLY=false \
  -e SELENIUM_GRID__MAX_BROWSER_INSTANCES=4 \
  -e SELENIUM_GRID__SE_NODE_MAX_SESSIONS=1 \
  -e KUBERNETES__KUBECONFIG=/kube/config-local-k3s \
  --add-host=host.docker.inte.rnal:host-gateway \
  -e KUBERNETES__USE_HOST_DOCKER_INTERNAL=true \
  -e KUBERNETES__CONTEXT=k3s-selenium-grid \
  -e KUBERNETES__NAMESPACE=selenium-grid-dev \
  -e KUBERNETES__SELENIUM_GRID_SERVICE_NAME=selenium-grid \
  ghcr.io/catchnip/mcp-selenium-grid:latest
```

> Note: All environment variables have default values.

#### MCP Server configuration (mcp.json)

```json
{
  "mcpServers": {
    "mcp-selenium-grid": {
      "url": "http://localhost:8000",
      "headers": {
        "Authorization": "Bearer CHANGE_ME"
      }
    }
  }
}
```

```json
{
  "mcpServers": {
    "mcp-selenium-grid": {
      "url": "http://localhost:8000/mcp",
      "headers": {
        "Authorization": "Bearer CHANGE_ME"
      }
    }
  }
}
```

```json
{
  "mcpServers": {
    "mcp-selenium-grid": {
      "url": "http://localhost:8000/sse",
      "headers": {
        "Authorization": "Bearer CHANGE_ME"
      }
    }
  }
}
```

## 🤝 Contributing

For development setup, testing, and contribution guidelines, please see [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

MIT
