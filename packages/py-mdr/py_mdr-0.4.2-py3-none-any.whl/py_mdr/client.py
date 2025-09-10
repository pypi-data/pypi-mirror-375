import asyncio
import json
import logging
import re
import sys
import uuid
from os import getenv

import httpx
from httpx import RequestError

from py_mdr.ocsf_models.events.base_event import BaseEvent
from py_mdr.ocsf_models.objects.base_model import BaseModel


class MDRClient:
    """
    Represents a raw client that allows sending of arbitrary messages to the
    MDR hec interface.
    """

    @staticmethod
    def _validate_dataset_name(dataset_name: str) -> bool:
        """
        Checks that the provided dataset name complies with the requirements
        """
        return re.match("^[a-z_]+$", dataset_name) is not None

    @staticmethod
    def _validate_namespace(namespace: str) -> bool:
        """
        Checks that the provided namespace complies with the requirements
        """
        return re.match("^[a-z]{3}$", namespace) is not None

    def __init__(self,
                 dataset_name: str,
                 namespace: str,
                 host: str = getenv("MDR_HOST"),
                 token: str = getenv("MDR_TOKEN"),
                 ssl_verify: bool = True):
        """
        Initializes the client. It takes by default the host and token values from the environment variables "MDR_HOST"
        and "MDR_TOKEN" respectively.

        :param dataset_name: Name to identify the application in OpenSearch. It can only contain [a-z_] characters.
        :param namespace: Namespace of the application to send the information into. Can only contain [a-z] characters and be 3 character long
        :param host: Hostname, with port, of where to send the log information (e.g. "host.name.tld:8080")
        :param token: Token for authenticating with the MDR client
        :param ssl_verify: If verify is enabled or not
        """
        # Validate dataset name and namespace
        if not self._validate_dataset_name(dataset_name):
            raise RuntimeError(f"Invalid dataset name provided: {dataset_name}. Must only contain [a-z_] characters.")

        if not self._validate_namespace(namespace):
            raise RuntimeError(
                f"Invalid namespace provided: {namespace}. Must contain three characters in the set [a-z].")

        self.source_name = f"SBP.pymdr::{dataset_name}.{namespace}"
        self.url = f"https://{host}/services/collector/event"

        # According to documentation: https://docs.splunk.com/Documentation/SplunkCloud/9.3.2411/Data/AboutHECIDXAck#About_channels_and_sending_data
        # Channels should be unique per client are sent as a UUID. As to make it deterministic per client, UUIDv5 is used
        # with DNS namespace. Which is created out of the dataset name and namespace.
        client_channel_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{dataset_name}.{namespace}.schubergphilis.com")
        headers = {
            "Authorization": f"Splunk {token}",
            "X-Splunk-Request-Channel": str(client_channel_id)
        }

        self.token = token
        self.ssl_verify = ssl_verify
        # Set up internal logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False  # No propagate, in case of failures on MDRHandler this doesn't start an infinite loop
        self.logger.addHandler(logging.StreamHandler(stream=sys.stderr))
        # Initialize HTTP client
        self.client = httpx.AsyncClient(verify=self.ssl_verify, headers=headers)

    async def send(self, event: dict | BaseEvent):
        """
        Sends a new event to the MDR. The event should be a raw dictionary or a subclass of BaseEvent.
        :param event:
        :return:
        """
        response = None
        entry = {
            "source": self.source_name,
            "event": {
                "source_format": self.source_name,
                **(event.as_dict() if isinstance(event, BaseModel) else event)
            }
        }

        response = None  # Define the variable, so the exception handler can check on None
        try:
            response = await self.client.post(
                self.url,
                json=entry,
                timeout=5)
            response.raise_for_status()
            self.logger.debug("Sent event of type %s to MDR. Response: %s", type(event), response.text)
        except (RequestError, Exception) as e:
            self.logger.error("Exception while sending event to MDR (%s). Response: (%s)", e,
                              response.text if response else "<NO RESPONSE>")

    async def send_batch(self, events: list[dict | BaseEvent]):
        """
        Sends a batch of events to the MDR asynchronously. Each event should be a raw dictionary or a subclass of BaseEvent.
        :param events: List of events to send
        :return:
        """
        response = None
        events_string = ''.join(
            json.dumps({
                "source": self.source_name,
                "event": {
                    "source_format": self.source_name,
                    **(event.as_dict() if isinstance(event, BaseModel) else event)
                }
            }) for event in events
        )

        try:
            response = await self.client.post(
                self.url,
                content=events_string,
                timeout=5)
            response.raise_for_status()
            self.logger.debug("Sent batch of %d events to MDR. Response: %s", len(events), response.text)
        except (RequestError, Exception) as e:
            self.logger.error("Exception while sending batch to MDR (%s). Response: (%s)", e,
                              response.text if response else "<NO RESPONSE>")

    async def send_async(self, event: dict):
        await asyncio.to_thread(self.send, event)
