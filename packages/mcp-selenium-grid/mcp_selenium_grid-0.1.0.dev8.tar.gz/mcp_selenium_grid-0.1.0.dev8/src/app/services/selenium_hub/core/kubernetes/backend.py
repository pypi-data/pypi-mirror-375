import uuid
from os import environ
from typing import Any, Callable, override

from kubernetes.client import (
    AppsV1Api,
    CoreV1Api,
    V1Capabilities,
)
from kubernetes.client.exceptions import ApiException
from kubernetes.client.models import (
    V1Container,
    V1ContainerPort,
    V1Deployment,
    V1DeploymentSpec,
    V1EnvVar,
    V1ExecAction,
    V1LabelSelector,
    V1Namespace,
    V1ObjectMeta,
    V1Pod,
    V1PodSecurityContext,
    V1PodSpec,
    V1PodTemplateSpec,
    V1Probe,
    V1ResourceRequirements,
    V1SeccompProfile,
    V1SecurityContext,
    V1Service,
    V1ServicePort,
    V1ServiceSpec,
)

from ...common.logger import logger
from ...models.browser import BrowserConfig, BrowserConfigs, BrowserType
from ...models.general_settings import SeleniumHubGeneralSettings
from ..hub_backend import HubBackend
from .common.auth import get_encoded_auth
from .common.constants import HTTP_NOT_FOUND
from .common.decorators import ErrorStrategy, handle_kubernetes_exceptions
from .k8s_config import KubernetesConfigManager
from .k8s_models import ResourceType, WaitConfig
from .k8s_port_forwarder import PortForwardManager
from .k8s_resource_manager import KubernetesResourceManager
from .k8s_url_resolver import KubernetesUrlResolver

HTTP_OK = 200


class KubernetesHubBackend(HubBackend):
    """
    Backend for managing Selenium Hub on Kubernetes.
    Handles cleanup and resource management for Selenium Hub deployments.
    """

    settings: SeleniumHubGeneralSettings
    config_manager: KubernetesConfigManager
    k8s_core: CoreV1Api
    k8s_apps: AppsV1Api
    resource_manager: KubernetesResourceManager
    url_resolver: KubernetesUrlResolver
    port_forward_manager: PortForwardManager | None

    def __init__(self, settings: SeleniumHubGeneralSettings) -> None:
        """Initialize the KubernetesHubBackend with the given settings."""
        self.settings = settings

        # Initialize components
        self.config_manager = KubernetesConfigManager(settings.kubernetes)
        self.k8s_core = CoreV1Api()
        self.k8s_apps = AppsV1Api()
        self.resource_manager = KubernetesResourceManager(
            settings.kubernetes, self.k8s_core, self.k8s_apps
        )
        self.url_resolver = KubernetesUrlResolver(
            settings, self.k8s_core, self.config_manager.is_kind
        )

        # Port-forwarding
        self.port_forward_manager = None

    @property
    def URL(self) -> str:
        """Get the Selenium Hub URL."""
        return self.url_resolver.get_hub_url()

    def cleanup_hub(self) -> None:
        """Clean up Selenium Hub deployment and service."""
        try:
            self.resource_manager.delete_resource(
                ResourceType.DEPLOYMENT, self.settings.kubernetes.SELENIUM_GRID_SERVICE_NAME
            )
        except Exception as e:
            logger.exception(f"Exception during deletion of deployment: {e}")

        try:
            self.resource_manager.delete_resource(
                ResourceType.SERVICE, self.settings.kubernetes.SELENIUM_GRID_SERVICE_NAME
            )
        except Exception as e:
            logger.exception(f"Exception during deletion of service: {e}")

    @handle_kubernetes_exceptions(ErrorStrategy.GRACEFUL)
    def cleanup_browsers(self) -> None:
        """Clean up all browser pods."""
        logger.info(
            f"Deleting {self.settings.NODE_LABEL} pods in namespace {self.settings.kubernetes.NAMESPACE}..."
        )
        self.k8s_core.delete_collection_namespaced_pod(
            namespace=self.settings.kubernetes.NAMESPACE,
            label_selector=f"app={self.settings.NODE_LABEL}",
        )
        logger.info(f"{self.settings.NODE_LABEL} pods delete request sent.")

    @override
    def cleanup(self) -> None:
        """Clean up all resources by first cleaning up browsers then the hub."""
        self._stop_service_port_forward()
        super().cleanup()

    def _validate_deployment_config(self, deployment: V1Deployment) -> bool:
        """Validate deployment configuration."""
        try:
            if not self._has_valid_spec_structure(deployment):
                return False

            if not self._has_valid_resource_limits(deployment):
                return False

            if (
                deployment.spec is None
                or deployment.spec.template is None
                or deployment.spec.template.spec is None
                or not deployment.spec.template.spec.security_context
            ):
                logger.warning("Deployment missing security context")
                return False

            return True
        except Exception as e:
            logger.error(f"Error validating deployment: {e}")
            return False

    def _has_valid_spec_structure(self, deployment: V1Deployment) -> bool:
        """Check if deployment has valid spec structure."""
        if (
            deployment.spec is None
            or deployment.spec.template is None
            or deployment.spec.template.spec is None
        ):
            logger.warning("Invalid deployment spec structure")
            return False
        return True

    def _has_valid_resource_limits(self, deployment: V1Deployment) -> bool:
        """Check if deployment has valid resource limits."""
        if (
            deployment.spec is None
            or deployment.spec.template is None
            or deployment.spec.template.spec is None
            or deployment.spec.template.spec.containers is None
        ):
            logger.warning("Invalid deployment spec structure for resource limits")
            return False
        for container in deployment.spec.template.spec.containers:
            if not container.resources or not container.resources.limits:
                logger.warning("Deployment missing resource limits")
                return False

            required_limits = ["cpu", "memory"]
            if not all(key in container.resources.limits for key in required_limits):
                logger.warning("Deployment missing required resource limits")
                return False
        return True

    def _validate_service_config(self, service: V1Service) -> bool:
        """Validate service configuration."""
        try:
            if not service.spec:
                logger.warning("Invalid service spec structure")
                return False

            if service.spec.type not in ["ClusterIP", "NodePort"]:
                logger.warning("Invalid service type")
                return False

            if not service.spec.ports:
                logger.warning("Service missing port configuration")
                return False

            required_attrs = ["port", "target_port"]
            for port in service.spec.ports:
                if not all(hasattr(port, attr) for attr in required_attrs):
                    logger.warning("Service port missing required attributes")
                    return False

            return True
        except Exception as e:
            logger.error(f"Error validating service: {e}")
            return False

    @handle_kubernetes_exceptions(ErrorStrategy.STRICT)
    def ensure_resource_exists(
        self,
        resource_type: ResourceType,
        name: str,
        create_func: Callable[..., Any],
        validate_func: Callable[..., Any] | None = None,
    ) -> None:
        """Generic method to ensure a resource exists."""
        try:
            self.resource_manager.read_resource(resource_type, name)
            logger.info(f"{name} {resource_type.value} already exists.")
        except ApiException as e:
            if e.status == HTTP_NOT_FOUND:
                logger.info(f"{name} {resource_type.value} not found, creating...")
                resource = create_func()

                if validate_func and not validate_func(resource):
                    raise ValueError(f"Invalid {resource_type.value} configuration")

                if resource_type == ResourceType.DEPLOYMENT:
                    self.k8s_apps.create_namespaced_deployment(
                        namespace=self.settings.kubernetes.NAMESPACE, body=resource
                    )
                elif resource_type == ResourceType.SERVICE:
                    self.k8s_core.create_namespaced_service(
                        namespace=self.settings.kubernetes.NAMESPACE, body=resource
                    )
                elif resource_type == ResourceType.NAMESPACE:
                    self.k8s_core.create_namespace(body=resource)

                logger.info(f"{name} {resource_type.value} created.")
            else:
                raise

    async def _ensure_deployment_exists(self) -> None:
        """Ensure the Selenium Hub deployment exists."""
        self.ensure_resource_exists(
            ResourceType.DEPLOYMENT,
            self.settings.kubernetes.SELENIUM_GRID_SERVICE_NAME,
            self._create_hub_deployment,
            self._validate_deployment_config,
        )

    async def _ensure_service_exists(self) -> None:
        """Ensure the Selenium Hub service exists."""
        self.ensure_resource_exists(
            ResourceType.SERVICE,
            self.settings.kubernetes.SELENIUM_GRID_SERVICE_NAME,
            self._create_hub_service,
            self._validate_service_config,
        )

    async def _ensure_namespace_exists(self) -> None:
        """Ensure the Kubernetes namespace exists."""
        self.ensure_resource_exists(
            ResourceType.NAMESPACE,
            self.settings.kubernetes.NAMESPACE,
            self._create_namespace,
            None,  # No validation needed for namespace
        )

    def _create_namespace(self) -> V1Namespace:
        """Create a Kubernetes Namespace object."""
        return V1Namespace(metadata=V1ObjectMeta(name=self.settings.kubernetes.NAMESPACE))

    async def _wait_for_service_ready(self, timeout_seconds: int = 30) -> None:
        """Wait for the service to be ready and have endpoints."""
        config = WaitConfig(timeout_seconds=timeout_seconds)
        await self.resource_manager.wait_for_resource_ready(
            ResourceType.SERVICE,
            self.settings.kubernetes.SELENIUM_GRID_SERVICE_NAME,
            None,  # Use default service ready check
            config,
        )

    async def ensure_hub_running(self) -> bool:
        """Ensure the Selenium Hub deployment and service exist in the namespace."""
        for i in range(self.settings.kubernetes.MAX_RETRIES):
            try:
                await self._ensure_namespace_exists()

                # First ensure deployment exists (this creates pods)
                await self._ensure_deployment_exists()

                # Wait for pod is ready
                await self._wait_for_hub_pod_ready()

                # Then ensure service exists (this exposes the pods)
                await self._ensure_service_exists()

                # Wait for service to be ready (this ensures NodePort is assigned)
                await self._wait_for_service_ready()

                # Start service port foward, if is KinD (Kubernetes in Docker)
                if self.config_manager.is_kind:
                    await self._start_service_port_forward()

                return True
            except Exception as e:
                logger.exception(f"Attempt {i + 1} to ensure K8s hub failed: {e}")
                if i < self.settings.kubernetes.MAX_RETRIES - 1:
                    await self.resource_manager.sleep(i)
                else:
                    logger.exception("Max retries reached for ensuring K8s hub.")
                    return False

        return False

    async def _wait_for_hub_pod_ready(self, timeout_seconds: int = 60) -> None:
        """Wait until the Selenium Hub pod is running and ready."""
        pod_name = self._get_hub_pod_name()
        config = WaitConfig(timeout_seconds=timeout_seconds)
        await self.resource_manager.wait_for_resource_ready(
            ResourceType.POD,
            pod_name,
            self._is_hub_pod_ready,
            config,
        )

    def _get_hub_pod_name(self) -> str:
        """Get the hub pod name using label selector."""
        pods = self.k8s_core.list_namespaced_pod(
            namespace=self.settings.kubernetes.NAMESPACE,
            label_selector=f"app={self.settings.kubernetes.SELENIUM_GRID_SERVICE_NAME}",
        )
        if not pods.items:
            raise RuntimeError("No hub pods found")
        pod = pods.items[0]
        if pod.metadata is None or pod.metadata.name is None:
            raise RuntimeError("Pod metadata or name is None")
        return pod.metadata.name

    def _is_hub_pod_ready(self, resource: Any) -> bool:
        """Check if hub pod is running and ready."""
        if not isinstance(resource, V1Pod):
            return False
        if not resource.status or not resource.metadata:
            return False

        if resource.status.phase == "Failed":
            raise RuntimeError(f"Pod {resource.metadata.name} failed to start.")

        return (
            resource.status.phase == "Running"
            and resource.status.container_statuses is not None
            and all(cs.ready for cs in resource.status.container_statuses)
        )

    async def create_browsers(
        self,
        count: int,
        browser_type: BrowserType,
        browser_configs: BrowserConfigs,
    ) -> list[str]:
        """Create the requested number of Selenium browser pods of the given type."""
        browser_ids: list[str] = []
        config: BrowserConfig = browser_configs[browser_type]

        for _ in range(count):
            for i in range(self.settings.kubernetes.MAX_RETRIES):
                try:
                    pod_name = f"{self.settings.NODE_LABEL}-{browser_type}-{uuid.uuid4().hex[:8]}"
                    pod = self._create_browser_pod(pod_name, browser_type, config)

                    await self._create_browser_pod_with_retry(pod_name, pod, i)
                    browser_ids.append(pod_name)
                    break
                except Exception as e:
                    logger.exception(f"Unexpected error creating browser pod: {e}")
                    if i < self.settings.kubernetes.MAX_RETRIES - 1:
                        await self.resource_manager.sleep(i)
                    else:
                        logger.exception(
                            "Max retries reached for creating browser pod due to unexpected error."
                        )
            else:
                logger.error("Failed to create browser pod after all retries.")

        return browser_ids

    @handle_kubernetes_exceptions(ErrorStrategy.STRICT)
    async def _create_browser_pod_with_retry(self, pod_name: str, pod: V1Pod, attempt: int) -> None:
        """Create a browser pod with retry logic."""
        self.k8s_core.create_namespaced_pod(namespace=self.settings.kubernetes.NAMESPACE, body=pod)
        logger.info(f"Pod {pod_name} created.")

    def _create_browser_pod(
        self, pod_name: str, browser_type: BrowserType, config: BrowserConfig
    ) -> V1Pod:
        """Create a browser pod configuration."""
        return V1Pod(
            metadata=V1ObjectMeta(
                name=pod_name,
                labels={
                    "app": self.settings.NODE_LABEL,
                    self.settings.BROWSER_LABEL: browser_type.value,
                },
            ),
            spec=V1PodSpec(
                containers=[
                    V1Container(
                        name=f"{self.settings.NODE_LABEL}-{browser_type}",
                        image=config.image,
                        ports=[V1ContainerPort(container_port=config.port)],
                        env=self._get_browser_env_vars(),
                        resources=V1ResourceRequirements(
                            limits={
                                "cpu": config.resources.cpu,
                                "memory": config.resources.memory,
                            },
                            requests={
                                "cpu": config.resources.cpu,
                                "memory": config.resources.memory,
                            },
                        ),
                    )
                ]
            ),
        )

    def _get_browser_env_vars(self) -> list[V1EnvVar]:
        """Get environment variables for browser containers."""
        return [
            V1EnvVar(
                name="SE_EVENT_BUS_HOST",
                value=self.settings.kubernetes.SELENIUM_GRID_SERVICE_NAME,
            ),
            V1EnvVar(
                name="SE_VNC_NO_PASSWORD",
                value=self.settings.selenium_grid.VNC_PASSWORD.get_secret_value(),
            ),
            V1EnvVar(
                name="SE_OPTS",
                value=f"--username {self.settings.selenium_grid.USER.get_secret_value()} \
                    --password {self.settings.selenium_grid.PASSWORD.get_secret_value()}",
            ),
        ]

    def _create_hub_deployment(self) -> V1Deployment:
        """Create a Kubernetes Deployment object for the Selenium Hub."""
        pod_security_context = V1PodSecurityContext(
            run_as_non_root=True,
            run_as_user=1001,
            fs_group=1001,
            seccomp_profile=V1SeccompProfile(type="RuntimeDefault"),
        )

        container_security_context = V1SecurityContext(
            allow_privilege_escalation=False,
            capabilities=V1Capabilities(drop=["ALL"]),
            run_as_non_root=True,
            run_as_user=1001,
            seccomp_profile=V1SeccompProfile(type="RuntimeDefault"),
        )

        container = V1Container(
            name=self.settings.HUB_NAME,
            image=self.settings.selenium_grid.HUB_IMAGE,
            ports=[V1ContainerPort(container_port=self.settings.selenium_grid.SELENIUM_HUB_PORT)],
            env=self._get_hub_env_vars(),
            resources=V1ResourceRequirements(
                requests={"cpu": "0.5", "memory": "256Mi"},
                limits={"cpu": "1", "memory": "500Mi"},
            ),
            security_context=container_security_context,
            startup_probe=V1Probe(
                _exec=V1ExecAction(
                    command=[
                        "/bin/sh",
                        "-c",
                        f"curl -s -o /dev/null -w '%{{http_code}}' -H 'Authorization: Basic {get_encoded_auth(self.settings)}' http://localhost:{self.settings.selenium_grid.SELENIUM_HUB_PORT}/status",
                    ]
                ),
                initial_delay_seconds=5,
                period_seconds=5,
                timeout_seconds=3,
                failure_threshold=30,
                success_threshold=1,
            ),
            readiness_probe=V1Probe(
                _exec=V1ExecAction(
                    command=[
                        "/bin/sh",
                        "-c",
                        f"curl -s -o /dev/null -w '%{{http_code}}' -H 'Authorization: Basic {get_encoded_auth(self.settings)}' http://localhost:{self.settings.selenium_grid.SELENIUM_HUB_PORT}/status",
                    ]
                ),
                initial_delay_seconds=5,
                period_seconds=10,
                timeout_seconds=5,
                failure_threshold=3,
                success_threshold=1,
            ),
        )

        template = V1PodTemplateSpec(
            metadata=V1ObjectMeta(
                labels={"app": self.settings.kubernetes.SELENIUM_GRID_SERVICE_NAME}
            ),
            spec=V1PodSpec(
                containers=[container],
                security_context=pod_security_context,
            ),
        )

        spec = V1DeploymentSpec(
            replicas=1,
            template=template,
            selector=V1LabelSelector(
                match_labels={"app": self.settings.kubernetes.SELENIUM_GRID_SERVICE_NAME}
            ),
        )

        return V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=V1ObjectMeta(
                name=self.settings.kubernetes.SELENIUM_GRID_SERVICE_NAME,
                namespace=self.settings.kubernetes.NAMESPACE,
            ),
            spec=spec,
        )

    def _get_hub_env_vars(self) -> list[V1EnvVar]:
        """Get environment variables for hub container."""
        return [
            V1EnvVar(
                name="SE_EVENT_BUS_HOST",
                value=self.settings.kubernetes.SELENIUM_GRID_SERVICE_NAME,
            ),
            V1EnvVar(name="SE_PORT", value=str(self.settings.selenium_grid.SELENIUM_HUB_PORT)),
            V1EnvVar(name="SE_EVENT_BUS_PUBLISH_PORT", value="4442"),
            V1EnvVar(name="SE_EVENT_BUS_SUBSCRIBE_PORT", value="4443"),
            V1EnvVar(
                name="SE_OPTS",
                value=f"--username {self.settings.selenium_grid.USER.get_secret_value()} \
                    --password {self.settings.selenium_grid.PASSWORD.get_secret_value()}",
            ),
            V1EnvVar(
                name="SE_VNC_NO_PASSWORD",
                value=self.settings.selenium_grid.VNC_VIEW_ONLY_STR,
            ),
            V1EnvVar(
                name="SE_VNC_PASSWORD",
                value=self.settings.selenium_grid.VNC_PASSWORD.get_secret_value(),
            ),
            V1EnvVar(
                name="SE_VNC_VIEW_ONLY",
                value=self.settings.selenium_grid.VNC_VIEW_ONLY_STR,
            ),
        ]

    def _create_hub_service(self) -> V1Service:
        """Create a Kubernetes Service object for the Selenium Hub."""
        service_type = "ClusterIP" if "KUBERNETES_SERVICE_HOST" in environ else "NodePort"

        spec = V1ServiceSpec(
            selector={"app": self.settings.kubernetes.SELENIUM_GRID_SERVICE_NAME},
            ports=[
                V1ServicePort(
                    port=self.settings.selenium_grid.SELENIUM_HUB_PORT,
                    target_port=self.settings.selenium_grid.SELENIUM_HUB_PORT,
                )
            ],
            type=service_type,
        )

        return V1Service(
            api_version="v1",
            kind="Service",
            metadata=V1ObjectMeta(
                name=self.settings.kubernetes.SELENIUM_GRID_SERVICE_NAME,
                namespace=self.settings.kubernetes.NAMESPACE,
            ),
            spec=spec,
        )

    @handle_kubernetes_exceptions(ErrorStrategy.RETURN_FALSE)
    async def delete_browser(self, browser_id: str) -> bool:
        """Delete a specific browser pod by its ID (pod name)."""
        self.resource_manager.delete_resource(ResourceType.POD, browser_id)
        return True

    async def _start_service_port_forward(self) -> None:
        """Start kubectl port-forward for the Selenium Hub service, with health check and retries."""
        if self.port_forward_manager:
            return
        pfm = PortForwardManager(
            service_name=self.settings.kubernetes.SELENIUM_GRID_SERVICE_NAME,
            namespace=self.settings.kubernetes.NAMESPACE,
            local_port=self.settings.kubernetes.PORT_FORWARD_LOCAL_PORT,
            remote_port=self.settings.selenium_grid.SELENIUM_HUB_PORT,
            kubeconfig=self.settings.kubernetes.KUBECONFIG,
            context=self.settings.kubernetes.CONTEXT,
            check_health=lambda: self.check_hub_health(
                username=self.settings.selenium_grid.USER.get_secret_value(),
                password=self.settings.selenium_grid.PASSWORD.get_secret_value(),
            ),
            max_retries=5,
            health_timeout=30,
        )
        if await pfm.start():
            self.port_forward_manager = pfm  # keep reference for later stop
        else:
            self.port_forward_manager = None
            raise RuntimeError("Failed to start port-forward and connect to Selenium Hub.")

    def _stop_service_port_forward(self) -> None:
        if self.port_forward_manager:
            self.port_forward_manager.stop()
            self.port_forward_manager = None
            logger.info("Stopped kubectl service port-forward.")
