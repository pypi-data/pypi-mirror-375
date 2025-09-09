"""Dedicated endpoint management for Together AI models.

This module provides comprehensive functionality for managing Together AI dedicated endpoints,
including creation, monitoring, lifecycle management, and text generation capabilities.

Key features:
- Automatic endpoint provisioning and configuration
- State monitoring and health checks
- Hardware configuration management
- Text generation with endpoint validation
- Robust error handling and logging

Classes:
    GenerateConfig: Configuration for text generation requests
    EndpointConfig: Configuration for endpoint creation and management
    EndpointClient: Main client for endpoint operations

Example:
    from together_ai_api_helper.endpoints import EndpointClient, EndpointConfig

    client = EndpointClient()
    config = EndpointConfig(
        model_name="mistralai/Mistral-7B-Instruct-v0.1",
        display_name="My Mistral Endpoint"
    )
    endpoint_name, endpoint_id = client.get_endpoint_for_model(config)

    # Generate text
    gen_config = GenerateConfig(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        system_prompt="You are a helpful assistant.",
        user_prompt="Hello, how are you?"
    )
    response = client.generate(endpoint_id, gen_config)
"""

import json
import os
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, cast

from pydantic import BaseModel
from together import Together
from together.types import DedicatedEndpoint
from together.types.endpoints import ListEndpoint

from .common import CommonClient


def _flatten_part_of_a_dict(
    d: dict[str, list[ListEndpoint]], key_list: tuple[str, ...]
) -> list[ListEndpoint]:
    """Flatten a dictionary of endpoint lists based on specified keys."""
    return sum((endpoints for status, endpoints in d.items() if status in key_list), [])


def _get_dict_of_endoint_id_and_model(endpoints: list[ListEndpoint]) -> dict[str, str]:
    """Create a mapping of endpoint IDs to their deployed models."""
    return {endpoint.id: endpoint.model for endpoint in endpoints}


class EndpointConfig(BaseModel):
    """Configuration for endpoint creation and management.

    Attributes:
        model_name: Name of the model to deploy on the endpoint.
            The model name is the same name returned by the training client.
            It usually looks like "username/model-suffix-a_set_of_random_numbers".
        display_name: Optional human-readable name for the endpoint
        hardware: Hardware configuration, defaults to the cheapest compatible hardware
        min_replicas: Minimum number of replicas to run, defaults to 1
        max_replicas: Maximum number of replicas to run, defaults to 1
        state: State of the endpoint, defaults to STARTED. Can be one of: STARTED, STOPPED
        inactive_timeout: Inactive timeout in minutes, defaults to 10
    """

    model_name: str
    display_name: str | None = None
    hardware: str | None = None
    min_replicas: int = 1
    max_replicas: int = 1
    state: str = "STARTED"
    inactive_timeout: int = 10


TIMEOUT_SECONDS_DELETION = 20
TIMEOUT_SECONDS_WAIT_FOR_STATE = 20 * 60

ENDPOINTS_STATES_ACTIVE = (
    "PENDING",
    "STARTING",
    "STARTED",
)
ENDPOINTS_STATES_INACTIVE = (
    "STOPPING",
    "STOPPED",
)
ENDPOINTS_STATES_FAILED = (
    "FAILED",
    "ERROR",
)
ENDPOINTS_STATES_ALL = ENDPOINTS_STATES_ACTIVE + ENDPOINTS_STATES_INACTIVE + ENDPOINTS_STATES_FAILED


def convert_endpoint_id_to_name(func: Callable[..., str]) -> Callable[..., tuple[str, str]]:
    """Decorator that converts endpoint ID return values to (name, id) tuples."""

    @wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> tuple[str, str]:
        endpoint_id = func(self, *args, **kwargs)
        # This is a hack to get the endpoint name from the endpoint ID
        # cause the Together API doesn't return the endpoint name :(
        os.system(
            "together endpoints list --type dedicated --json > _tmp_endpoints.json 2>/dev/null"
        )
        with open("_tmp_endpoints.json", encoding="utf-8") as f:
            endpoints = json.load(f)
        os.system("rm _tmp_endpoints.json")

        for endpoint in endpoints:
            if "id" not in endpoint:
                continue
            if endpoint["id"] == endpoint_id:
                return endpoint["name"], endpoint["id"]
        raise ValueError(f"Endpoint {endpoint_id} not found")

    return wrapper


class EndpointClient(CommonClient):
    """Client for managing Together AI dedicated endpoints.

    This client provides comprehensive endpoint management including creation,
    monitoring, lifecycle management, and text generation capabilities.
    """

    def __init__(
        self,
        client: Together | None = None,
        log_file: str | None = "endpoints.log",
        log_level: int | None = None,
    ):
        """Initialize the endpoint client.

        Args:
            client: Optional Together client instance (creates new one if None)
            log_file: Path to log file for endpoint operations, defaults to "endpoints.log".
                If log_file is None, no log file will be created.
            log_level: The level of the logger, defaults to INFO.
        """
        super().__init__("endpoints", client, log_file, log_level)

    def get_cheapest_hardware(self, model_name: str) -> str:
        """Get the cheapest hardware configuration for the given model."""
        available_hardware = self.client.endpoints.list_hardware(model=model_name)
        if not available_hardware:
            self.logger.error("No hardware found for model %s", model_name)
            raise ValueError(f"No hardware found for model {model_name}")
        cheapest_hardware = sorted(available_hardware, key=lambda x: x.pricing.cents_per_minute)[
            0
        ].id
        return cast(str, cheapest_hardware)

    @convert_endpoint_id_to_name
    def get_endpoint_for_model(self, endpoint_config: EndpointConfig) -> str:
        """Get the model name and endpoint id for the given model configuration."""
        model_name = endpoint_config.model_name
        display_name = endpoint_config.display_name
        self.logger.info(
            "Getting endpoint for model %s with display name %s", model_name, display_name
        )
        if endpoint_config.hardware is None:
            # This is not great since I'm changing the endpoint config in place but it's simplest for now
            endpoint_config.hardware = self.get_cheapest_hardware(model_name)
        self.logger.info("Using hardware %s", endpoint_config.hardware)

        endpoint_ids_for_this_model = self.list_endpoints_for_model(model_name)

        if not endpoint_ids_for_this_model:
            self.logger.info("No endpoint found for model %s, creating a new one...", model_name)
            return self._create_endpoint(endpoint_config)

        if len(endpoint_ids_for_this_model) > 1:
            self.logger.error(
                "Multiple endpoints found for model %s: %s. Please delete the extra endpoints.",
                model_name,
                ", ".join(endpoint_ids_for_this_model),
            )
            raise ValueError(
                f"Multiple endpoints found for model {model_name}: {endpoint_ids_for_this_model}. "
                "Please delete the extra endpoints."
            )

        endpoint_id = endpoint_ids_for_this_model[0]
        self.logger.info("Found an existing endpoint %s for model %s", endpoint_id, model_name)

        if self.client.endpoints.get(endpoint_id).hardware != endpoint_config.hardware:
            self.logger.info(
                "Hardware mismatch, deleting endpoint %s and creating a new one...", endpoint_id
            )
            self.delete_endpoint(endpoint_id)
            return self._create_endpoint(endpoint_config)

        if (
            display_name is not None
            and self.client.endpoints.get(endpoint_id).display_name != display_name
        ):
            self.logger.info(
                "Display name mismatch, updating endpoint %s with display name %s...",
                endpoint_id,
                display_name,
            )
            self.client.endpoints.update(endpoint_id, display_name=display_name)

        state = self.client.endpoints.get(endpoint_id).state
        if state in ENDPOINTS_STATES_ACTIVE:
            self.logger.info("The endpoint is active (%s), returning it...", state)
            self._wait_for_state(endpoint_id, "STARTED")
            return endpoint_id
        if state in ENDPOINTS_STATES_INACTIVE:
            self.logger.info("The endpoint is inactive (%s), restarting it...", state)
            self.restart_endpoint(endpoint_id)
            return endpoint_id
        if state in ENDPOINTS_STATES_FAILED:
            self.logger.info(
                "The endpoint is failed (%s), deleting it and creating a new one...", state
            )
            self.delete_endpoint(endpoint_id)
            return self._create_endpoint(endpoint_config)
        raise ValueError(f"Endpoint {endpoint_id} is in an unexpected state: {state}")

    def _create_endpoint(self, endpoint_config: EndpointConfig) -> str:
        """Create a new dedicated endpoint with the specified configuration."""
        endpoint: DedicatedEndpoint = self.client.endpoints.create(
            model=endpoint_config.model_name,
            hardware=endpoint_config.hardware,
            min_replicas=endpoint_config.min_replicas,
            max_replicas=endpoint_config.max_replicas,
            display_name=endpoint_config.display_name,
            state=endpoint_config.state,
            inactive_timeout=endpoint_config.inactive_timeout,
        )
        self.logger.info(
            "Created a new endpoint %s for model %s", endpoint.id, endpoint_config.model_name
        )
        self._wait_for_state(endpoint.id, endpoint_config.state)
        return cast(str, endpoint.id)

    def _verify_endpoint_exists(self, endpoint_id: str) -> None:
        """Verify that an endpoint exists."""
        if endpoint_id not in self.list_all_endpoints():
            self.logger.error("Endpoint %s not found", endpoint_id)
            raise ValueError(f"Endpoint {endpoint_id} not found")

    def _verify_endpoint_active(self, endpoint_id: str) -> None:
        """Verify that an endpoint is in an active state."""
        if self.client.endpoints.get(endpoint_id).state not in ENDPOINTS_STATES_ACTIVE:
            self.logger.error("Endpoint %s is not active", endpoint_id)
            raise ValueError(f"Endpoint {endpoint_id} is not active")

    def _verify_endpoint_inactive(self, endpoint_id: str) -> None:
        """Verify that an endpoint is in an inactive state."""
        if self.client.endpoints.get(endpoint_id).state not in ENDPOINTS_STATES_INACTIVE:
            self.logger.error("Endpoint %s is not inactive", endpoint_id)
            raise ValueError(f"Endpoint {endpoint_id} is not inactive")

    def _wait_for_state(self, endpoint_id: str, state: str) -> None:
        """Wait for the endpoint to reach the specified state."""
        counter = 0
        increment = 0
        current_state = self.client.endpoints.get(endpoint_id).state
        while current_state != state:
            self.logger.info(
                "Waiting %ss for the %s to be %s, current state is %s (%ss passed)...",
                increment,
                endpoint_id,
                state,
                current_state,
                counter,
            )
            time.sleep(increment)
            counter += increment
            increment = min(increment + 5, 60)
            if counter > TIMEOUT_SECONDS_WAIT_FOR_STATE:
                self.logger.error(
                    "Endpoint %s not %s after %s seconds, current state is %s",
                    endpoint_id,
                    state,
                    TIMEOUT_SECONDS_WAIT_FOR_STATE,
                    current_state,
                )
                raise TimeoutError(
                    f"Endpoint {endpoint_id} not {state} after {TIMEOUT_SECONDS_WAIT_FOR_STATE} "
                    f"seconds, current state is {current_state}"
                )
            current_state = self.client.endpoints.get(endpoint_id).state
        self.logger.info("Endpoint %s is %s", endpoint_id, state)

    def print_status(self, endpoint_id: str, verbose: bool = False) -> None:
        """Print the current status of an endpoint.

        Args:
            endpoint_id: ID of the endpoint to check
            verbose: If True, prints full endpoint information
        """
        if endpoint_id not in self.list_all_endpoints():
            self.logger.info("Endpoint %s is not found", endpoint_id)
            return
        endpoint = self.client.endpoints.get(endpoint_id)
        self.logger.info("Endpoint %s is %s", endpoint_id, endpoint.state)
        if verbose:
            self.logger.info("Endpoint %s full info: %s", endpoint_id, endpoint)

    def restart_endpoint(self, endpoint_id: str) -> None:
        """Restart an inactive endpoint."""
        self._verify_endpoint_exists(endpoint_id)
        self._verify_endpoint_inactive(endpoint_id)
        self.client.endpoints.update(endpoint_id, state="STARTED")
        self._wait_for_state(endpoint_id, "STARTED")

    def stop_endpoint(self, endpoint_id: str) -> None:
        """Stop an active endpoint."""
        self._verify_endpoint_exists(endpoint_id)
        self._verify_endpoint_active(endpoint_id)
        self.client.endpoints.update(endpoint_id, state="STOPPED")
        self._wait_for_state(endpoint_id, "STOPPED")

    def delete_endpoint(self, endpoint_id: str) -> None:
        """Delete an endpoint permanently."""
        self.logger.info("Deleting endpoint %s...", endpoint_id)
        self._verify_endpoint_exists(endpoint_id)
        self.client.endpoints.delete(endpoint_id)
        counter = 0
        while endpoint_id in self.list_all_endpoints():
            time.sleep(5)
            counter += 5
            self.logger.info(
                "Waiting for endpoint %s to be deleted (%s seconds passed)...", endpoint_id, counter
            )
            if counter > TIMEOUT_SECONDS_DELETION:
                self.logger.error(
                    "Endpoint %s not deleted after %s seconds",
                    endpoint_id,
                    TIMEOUT_SECONDS_DELETION,
                )
                raise TimeoutError(
                    f"Endpoint {endpoint_id} not deleted after {TIMEOUT_SECONDS_DELETION} seconds"
                )
        self.logger.info("Endpoint %s deleted", endpoint_id)

    def list_all_endpoints_with_states(self) -> dict[str, list[ListEndpoint]]:
        """Get all endpoints grouped by their current states.

        Returns:
            Dictionary mapping state names to lists of endpoints in that state

        Note:
            Includes all possible endpoint states: active, inactive, and failed.
        """
        endpoints = self.client.endpoints.list(type="dedicated")
        grouped_by_state = {
            state: [endpoint for endpoint in endpoints if endpoint.state == state]
            for state in ENDPOINTS_STATES_ALL
        }
        return grouped_by_state

    def list_endpoints_for_model(self, model: str) -> list[str]:
        """List all endpoint IDs that are running the specified model."""
        return [id_ for id_, model_ in self.list_all_endpoints().items() if model_ == model]

    def list_active_endpoints(self) -> dict[str, str]:
        """List all endpoints that are currently active (PENDING, STARTING, STARTED)."""
        return _get_dict_of_endoint_id_and_model(
            _flatten_part_of_a_dict(self.list_all_endpoints_with_states(), ENDPOINTS_STATES_ACTIVE)
        )

    def list_inactive_endpoints(self) -> dict[str, str]:
        """List all endpoints that are currently inactive (STOPPING, STOPPED)."""
        return _get_dict_of_endoint_id_and_model(
            _flatten_part_of_a_dict(
                self.list_all_endpoints_with_states(), ENDPOINTS_STATES_INACTIVE
            )
        )

    def list_all_endpoints(self) -> dict[str, str]:
        """List all endpoints regardless of their state."""
        return _get_dict_of_endoint_id_and_model(
            _flatten_part_of_a_dict(self.list_all_endpoints_with_states(), ENDPOINTS_STATES_ALL)
        )
