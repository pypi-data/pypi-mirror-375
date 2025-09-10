"""Selenium Hub service for managing browser instances."""

from __future__ import annotations

import asyncio
from urllib.parse import urljoin

from app.services.metrics import track_browser_metrics, track_hub_metrics  # TODO: refactor and test

from .manager import SeleniumHubManager
from .models.browser import BrowserType
from .models.general_settings import SeleniumHubGeneralSettings


class SeleniumHub:
    """
    Service for managing Selenium Grid Hub and Node instances via manager/adaptor pattern.

    This class implements the Singleton pattern to ensure only one instance manages the Selenium Grid Hub
    and its browser nodes across the application.

    The singleton instance is created on first instantiation and reused for subsequent calls.
    The initialization of instance variables only happens once, even if the constructor is called multiple times.
    SeleniumHubBaseSettings provided after initialization will update the existing instance.

    Attributes:
        settings (SeleniumHubBaseSettings): Application settings used to configure the hub and browsers
        _manager (SeleniumHubManager): Manager instance that handles the actual hub operations
        browser_configs (BrowserConfigs): Configuration for supported browser types

    Class Variables:
        _instance (SeleniumHub | None): The singleton instance of the class
        _initialized (bool): Flag indicating whether the instance has been initialized
    """

    _instance: SeleniumHub | None = None
    _initialized: bool = False

    def __new__(cls, settings: SeleniumHubGeneralSettings | None = None) -> "SeleniumHub":
        """
        Create or return the singleton instance.

        Args:
            settings (SeleniumHubGeneralSettings | None): Application settings. Required for first initialization.

        Returns:
            SeleniumHub: The singleton instance

        Raises:
            ValueError: If settings is None during first initialization
        """
        if cls._instance is None:
            if settings is None:
                raise ValueError("settings must be provided for first initialization")
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, settings: SeleniumHubGeneralSettings | None = None) -> None:
        """
        Initialize or update the singleton instance.

        If this is the first initialization:
        - Creates a new instance with the provided settings
        - Initializes the manager and browser configs

        If the instance already exists:
        - Updates the settings using Pydantic's model methods
        - Reinitializes the manager with new settings
        - Updates browser configs if needed

        Args:
            settings (SeleniumHubBaseSettings | None): Application settings. Required for first initialization.

        Raises:
            ValueError: If settings is None during first initialization
            ValidationError: If any of the updated values are invalid
        """
        if not self._initialized:
            if settings is None:
                raise ValueError("Settings must be provided for first initialization")
            self.settings: SeleniumHubGeneralSettings = settings
            self._manager: SeleniumHubManager = SeleniumHubManager(self.settings)
            self._initialized = True
        elif settings is not None:
            # Update settings
            self.settings = settings

            # Reinitialize manager with updated settings
            self._manager = SeleniumHubManager(self.settings)

    @property
    def URL(self) -> str:
        """
        Get the base URL for the Selenium Hub.

        Returns:
            str: The base URL for the Selenium Hub
        """
        return self._manager.URL

    @property
    def WEBDRIVER_REMOTE_URL(self) -> str:
        """
        Get the URL to connect to the Grid's Hub or Router

        Returns:
            str: The URL to Remote WebDriver
        """
        return urljoin(self.URL, "/wd/hub")

    @track_hub_metrics()
    async def check_hub_health(self) -> bool:
        """
        Check if the Selenium Hub is healthy and reachable by polling the status endpoint.

        Returns:
            bool: True if the hub responds with 200 OK, False otherwise.
        """

        return await self._manager.check_hub_health(
            username=self.settings.selenium_grid.USER.get_secret_value(),
            password=self.settings.selenium_grid.PASSWORD.get_secret_value(),
        )

    @track_hub_metrics()
    async def ensure_hub_running(self) -> bool:
        """
        Ensure the hub container/service is running.
        This only checks if the container/service exists and is running.

        Returns:
            bool: True if the hub container/service is running, False otherwise.
        """
        return await self._manager.ensure_hub_running()

    @track_hub_metrics()
    async def wait_for_hub_healthy(
        self,
        wait_before_check: float = 0.0,
        check_interval: float = 1.0,
    ) -> bool:
        """
        Wait for the hub to be healthy and reachable.
        Uses asyncio.timeout() to limit the total wait time.

        Args:
            wait_before_check (float): Time before start checks.
            check_interval (float): Time between health checks in seconds.

        Returns:
            bool: True if the hub becomes healthy within the timeout, False otherwise.
        """
        try:
            await asyncio.sleep(wait_before_check)
            async with asyncio.timeout(30):  # 30 second default timeout
                while True:
                    if await self.check_hub_health():
                        return True
                    await asyncio.sleep(check_interval)
        except asyncio.TimeoutError:
            return False

    @track_browser_metrics()
    async def create_browsers(self, count: int, browser_type: BrowserType) -> list[str]:
        """
        Create the specified number of browser instances of the given type.

        Args:
            count (int): Number of browser instances to create
            browser_type (BrowserType): Type of browser to create (must be in browser_configs)

        Returns:
            list[str]: List of created browser IDs

        Raises:
            ValueError: If count is not positive or exceeds MAX_BROWSER_INSTANCES
            KeyError: If browser_type is not supported
        """
        if count <= 0:
            raise ValueError("Browser count must be positive")
        if browser_type not in self.settings.selenium_grid.BROWSER_CONFIGS:
            raise KeyError(f"Unsupported browser type: {browser_type}")
        if (
            self.settings.selenium_grid.MAX_BROWSER_INSTANCES
            and count > self.settings.selenium_grid.MAX_BROWSER_INSTANCES
        ):
            raise ValueError(
                f"Maximum browser instances exceeded: {count} > {self.settings.selenium_grid.MAX_BROWSER_INSTANCES}"
            )
        return await self._manager.create_browsers(
            count, browser_type, self.settings.selenium_grid.BROWSER_CONFIGS
        )

    @track_browser_metrics()
    async def delete_browsers(self, browser_ids: list[str]) -> list[str]:
        """
        Delete the specified browser instances.

        Args:
            browser_ids (list[str]): List of browser IDs to delete

        Returns:
            list[str]: List of successfully deleted browser IDs
        """
        if not browser_ids:
            return []
        return await self._manager.delete_browsers(browser_ids)

    def cleanup(self) -> None:
        """
        Clean up all resources managed by the Selenium Hub (containers, networks, etc.).
        Delegates to the manager's cleanup method.
        """
        self._manager.cleanup()
