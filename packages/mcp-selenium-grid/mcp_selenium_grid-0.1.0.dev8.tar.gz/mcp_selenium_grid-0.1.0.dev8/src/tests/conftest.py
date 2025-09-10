"""Pytest configuration file."""

from typing import Any, Callable, Generator, cast
from unittest.mock import MagicMock

import pytest
from app.common.shutil import which_or_raise
from app.core.settings import Settings
from app.dependencies import get_settings
from app.services.selenium_hub import SeleniumHub
from app.services.selenium_hub.core.docker_backend import DockerHubBackend
from app.services.selenium_hub.core.kubernetes import KubernetesHubBackend
from app.services.selenium_hub.models import DeploymentMode
from app.services.selenium_hub.models.browser import BrowserConfig, BrowserType, ContainerResources
from docker.errors import NotFound  # Add NotFound for mocking
from fastapi.testclient import TestClient
from httpx import BasicAuth
from pydantic import SecretStr
from pytest import FixtureRequest, MonkeyPatch
from pytest_mock import MockerFixture


def pytest_configure(config: Any) -> None:
    """Configure pytest."""
    # No deprecated asyncio_default_fixture_loop_scope config
    # No-op


# ==============================================================================
# UNIT TEST FIXTURES AND MOCKS
# ==============================================================================


@pytest.fixture(autouse=True)
def patch_sleep(mocker: MockerFixture, request: FixtureRequest) -> None:
    """Automatically patch sleep functions in k8s_backend module for all unit tests."""
    if "unit" in request.keywords:
        mocker.patch("time.sleep", return_value=None)
        mocker.patch(
            "asyncio.sleep",
            new_callable=mocker.AsyncMock,
        )


# DOCKER ========================================================================


def create_mock_container(
    mocker: MockerFixture,
    status: str = "running",
    name: str = "mock-container",
    id: str = "container-id",
    image_tags: list[str] | None = None,
) -> MagicMock:
    """Create a MagicMock Docker container with the given attributes."""
    if image_tags is None:
        image_tags = ["image:latest"]
    mock_container: MagicMock = mocker.MagicMock()
    mock_container.status = status
    mock_container.name = name
    mock_container.id = id
    mock_container.image = mocker.MagicMock(tags=image_tags)
    mock_container.attrs = {"Config": {"Image": image_tags[0]}}
    mock_container.remove = mocker.MagicMock()
    mock_container.restart = mocker.MagicMock()
    mock_container.reload = mocker.MagicMock()
    return mock_container


def create_mock_network(
    mocker: MockerFixture, name: str = "mock-network", id: str = "network-id"
) -> MagicMock:
    """Create a MagicMock Docker network with the given attributes."""
    mock_network: MagicMock = mocker.MagicMock()
    mock_network.name = name
    mock_network.id = id
    mock_network.remove = mocker.MagicMock()
    return mock_network


@pytest.fixture
def mock_docker_client(mocker: MockerFixture) -> MagicMock:
    """
    Single, DRY fixture for a fully mocked Docker client for all unit tests.
    Uses helper functions for per-test container/network customization.
    """
    client: MagicMock = mocker.MagicMock(name="DockerClientMock")
    # Containers
    containers = mocker.MagicMock(name="ContainersMock")
    containers.list.return_value = []
    containers.get.side_effect = containers.run.side_effect = containers.create.side_effect = (
        lambda *args, **kwargs: create_mock_container(mocker, *args, **kwargs)
    )
    client.containers = containers
    # Networks
    networks = mocker.MagicMock(name="NetworksMock")
    networks.list.return_value = []
    networks.get.side_effect = networks.create.side_effect = (
        lambda *args, **kwargs: create_mock_network(mocker, *args, **kwargs)
    )
    client.networks = networks
    # Images
    images = mocker.MagicMock(name="ImagesMock")
    images.get.return_value = mocker.MagicMock(name="ImageMock")
    images.pull.return_value = mocker.MagicMock(name="ImagePullMock")
    client.images = images
    # API
    api = mocker.MagicMock(name="ApiMock")
    api.create_container.return_value = {"Id": "mock-container-id"}
    api.create_network.return_value = {"Id": "mock-network-id"}
    client.api = api
    # Patch docker.from_env everywhere
    mocker.patch("docker.from_env", return_value=client)

    return client


@pytest.fixture
def docker_not_found() -> type:
    """Fixture to provide docker.errors.NotFound exception class for use in tests."""
    return NotFound


@pytest.fixture
def docker_hub_settings(mocker: MockerFixture) -> Settings:
    """Fixture to provide a mocked settings object for DockerHubBackend."""
    settings: Settings = cast(
        Settings,
        mocker.MagicMock(spec=Settings()),
    )

    # SeleniumHubGeneralSettings
    settings.DEPLOYMENT_MODE = DeploymentMode.DOCKER

    # Docker Settings (docker attribute) - only those used by tests
    settings.docker.DOCKER_NETWORK_NAME = "test-network"

    # Selenium Hub Settings (selenium_hub attribute) - only those used by tests
    settings.selenium_grid.USER = SecretStr("test-user")
    settings.selenium_grid.PASSWORD = SecretStr("test-password")
    settings.selenium_grid.SELENIUM_HUB_PORT = 4444
    settings.selenium_grid.MAX_BROWSER_INSTANCES = 8
    settings.selenium_grid.BROWSER_CONFIGS = {
        BrowserType.CHROME: BrowserConfig(
            image="selenium/node-chrome:latest",
            resources=ContainerResources(memory="512M", cpu="0.5"),
            port=4444,
        )
    }

    return settings


@pytest.fixture
def docker_backend(
    mock_docker_client: MagicMock,
    docker_hub_settings: Settings,
    mocker: MockerFixture,
) -> DockerHubBackend:
    """Fixture for DockerHubBackend with a mocked Docker client."""
    mocker.patch(
        "app.services.selenium_hub.core.docker_backend.docker.from_env",
        return_value=mock_docker_client,
    )
    return DockerHubBackend(docker_hub_settings)


# KUBERNETES ====================================================================


@pytest.fixture
def mock_k8s_apis(monkeypatch: MonkeyPatch, mocker: MockerFixture) -> tuple[MagicMock, MagicMock]:
    """
    Patches CoreV1Api and AppsV1Api so they use MagicMocks for the entire session.
    """
    # Patch kubernetes config loading functions and environment variables to prevent real K8s access
    mocker.patch("app.services.selenium_hub.core.kubernetes.k8s_config.load_incluster_config")
    mocker.patch("app.services.selenium_hub.core.kubernetes.k8s_config.load_kube_config")
    monkeypatch.delenv("KUBERNETES_SERVICE_HOST", raising=False)
    monkeypatch.delenv("KUBERNETES_SERVICE_PORT", raising=False)

    core_mock = mocker.patch("kubernetes.client.CoreV1Api").return_value
    apps_mock = mocker.patch("kubernetes.client.AppsV1Api").return_value

    return core_mock, apps_mock


@pytest.fixture
def k8s_hub_settings(mocker: MockerFixture) -> Settings:
    """Fixture to provide a mocked settings object for KubernetesHubBackend."""
    settings: Settings = cast(Settings, mocker.MagicMock(spec=Settings()))

    # SeleniumHubGeneralSettings
    settings.DEPLOYMENT_MODE = DeploymentMode.KUBERNETES

    # Selenium Hub Settings (selenium_hub attribute) - only those used by tests
    settings.selenium_grid.USER = SecretStr("test-user")
    settings.selenium_grid.PASSWORD = SecretStr("test-password")
    settings.selenium_grid.MAX_BROWSER_INSTANCES = 8
    settings.selenium_grid.SELENIUM_HUB_PORT = 4444
    settings.selenium_grid.BROWSER_CONFIGS = {
        BrowserType.CHROME: BrowserConfig(
            image="selenium/node-chrome:latest",
            resources=ContainerResources(memory="512M", cpu="0.5"),
            port=4444,
        )
    }

    # Kubernetes Settings (kubernetes attribute) - only those used by tests
    settings.kubernetes.NAMESPACE = "test-namespace"
    settings.kubernetes.SELENIUM_GRID_SERVICE_NAME = "test-service-name"
    settings.kubernetes.MAX_RETRIES = 3

    # Constants for resource names - only those used by tests
    settings.NODE_LABEL = "selenium-node"

    return settings


@pytest.fixture
def k8s_backend(
    mock_k8s_apis: tuple[MagicMock, MagicMock],
    k8s_hub_settings: Settings,
    mocker: MockerFixture,
) -> Generator[KubernetesHubBackend, None, None]:
    """Fixture that yields a KubernetesHubBackend instance with mocked K8s clients."""

    core, apps = mock_k8s_apis

    backend = KubernetesHubBackend(k8s_hub_settings)
    backend.k8s_core = core
    backend.k8s_apps = apps

    yield backend


# ==============================================================================
# INTEGRATION TEST FIXTURES
# ==============================================================================


@pytest.fixture
def selenium_hub_basic_auth_headers() -> BasicAuth:
    """Fixture to provide HTTP Basic Auth for Selenium Hub."""
    settings = get_settings()
    return BasicAuth(
        settings.selenium_grid.USER.get_secret_value(),
        settings.selenium_grid.PASSWORD.get_secret_value(),
    )


def create_cmd_fixture(name: str) -> Callable[[], str]:
    @pytest.fixture(name=name + "_path")
    def _fixture() -> str:
        return which_or_raise(name)

    return _fixture


uv_path = create_cmd_fixture("uv")
uvx_path = create_cmd_fixture("uvx")

# ==============================================================================
# E2E TEST FIXTURES
# ==============================================================================

# ==============================================================================
# SHARED TEST FIXTURES
# ==============================================================================


# Client fixture used by Integration and E2E tests
@pytest.fixture(scope="session", params=[DeploymentMode.DOCKER, DeploymentMode.KUBERNETES])
def client(request: FixtureRequest) -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app with dependency override for verify_token."""
    from app.main import create_application  # noqa: PLC0415
    from fastapi.testclient import TestClient  # noqa: PLC0415

    app = create_application()

    # Override settings based on deployment mode
    settings = get_settings()
    settings.DEPLOYMENT_MODE = request.param
    app.dependency_overrides[get_settings] = lambda: settings

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# Client fixture with API_TOKEN patched to empty string
@pytest.fixture(scope="session", params=[DeploymentMode.DOCKER, DeploymentMode.KUBERNETES])
def client_disabled_auth(request: FixtureRequest) -> Generator[TestClient, None, None]:
    from app.main import create_application  # noqa: PLC0415
    from fastapi.testclient import TestClient  # noqa: PLC0415

    app = create_application()

    # Override settings based on deployment mode
    settings = get_settings()
    settings.DEPLOYMENT_MODE = request.param

    # Disable Auth
    settings.AUTH_ENABLED = False

    app.dependency_overrides[get_settings] = lambda: settings

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def reset_selenium_hub_singleton() -> None:
    """Reset the SeleniumHub singleton instance."""
    SeleniumHub._instance = None
    SeleniumHub._initialized = False


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Create authentication headers for API requests."""
    return {"Authorization": f"Bearer {get_settings().API_TOKEN.get_secret_value()}"}
