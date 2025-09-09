# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Connection management for AWS services used by Amazon RDS MCP Server."""

import boto3
import os
from botocore.config import Config
from typing import Any, Optional, Dict


class BaseConnectionManager:
    """Base class for AWS service connection managers."""

    _client: Optional[Any] = None
    # Cache clients per service and region to avoid cross-service reuse
    _clients_by_region: Dict[str, Dict[str, Any]] = {}
    _service_name: str = ''  # Must be overridden by subclasses
    _env_prefix: str = ''  # Must be overridden by subclasses

    @classmethod
    def get_connection(cls, aws_region: Optional[str] = None) -> Any:
        """Get or create an AWS service client connection with retry capabilities.

        Returns:
            boto3.client: An AWS service client configured with retries
        """
        # When a region override is provided, maintain a separate client per
        # service and region
        if aws_region:
            service_cache = cls._clients_by_region.get(cls._service_name, {})
            if aws_region in service_cache:
                return service_cache[aws_region]

        if cls._client is None and not aws_region:
            # Get AWS configuration from environment
            # If AWS_PROFILE is not explicitly set, allow default credential chain
            aws_profile = os.environ.get('AWS_PROFILE')
            env_region = (
                os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION')
            )

            # Configure retry settings
            max_retries = int(os.environ.get(f'{cls._env_prefix}_MAX_RETRIES', '3'))
            retry_mode = os.environ.get(f'{cls._env_prefix}_RETRY_MODE', 'standard')
            connect_timeout = int(os.environ.get(f'{cls._env_prefix}_CONNECT_TIMEOUT', '5'))
            read_timeout = int(os.environ.get(f'{cls._env_prefix}_READ_TIMEOUT', '10'))

            # Create boto3 config with retry settings
            config = Config(
                retries={'max_attempts': max_retries, 'mode': retry_mode},
                connect_timeout=connect_timeout,
                read_timeout=read_timeout,
                # Identify requests from LLM/MCP
                user_agent_extra='MCP/AmazonRDSControlPlaneMCPServer',
            )

            # Initialize AWS session and client with config
            # If no profile is provided, rely on default credential chain
            if aws_profile:
                session = boto3.Session(
                    profile_name=aws_profile, region_name=env_region
                )
            else:
                session = boto3.Session(region_name=env_region)
            cls._client = session.client(
                service_name=cls._service_name, config=config
            )
        # If region override requested, build and cache a regional client
        if aws_region:
            aws_profile = os.environ.get('AWS_PROFILE')
            max_retries = int(os.environ.get(f'{cls._env_prefix}_MAX_RETRIES', '3'))
            retry_mode = os.environ.get(f'{cls._env_prefix}_RETRY_MODE', 'standard')
            connect_timeout = int(
                os.environ.get(f'{cls._env_prefix}_CONNECT_TIMEOUT', '5')
            )
            read_timeout = int(
                os.environ.get(f'{cls._env_prefix}_READ_TIMEOUT', '10')
            )
            config = Config(
                retries={'max_attempts': max_retries, 'mode': retry_mode},
                connect_timeout=connect_timeout,
                read_timeout=read_timeout,
                user_agent_extra='MCP/AmazonRDSControlPlaneMCPServer',
            )
            if aws_profile:
                session = boto3.Session(
                    profile_name=aws_profile, region_name=aws_region
                )
            else:
                session = boto3.Session(region_name=aws_region)
            client = session.client(service_name=cls._service_name, config=config)
            # insert into per-service cache
            if cls._service_name not in cls._clients_by_region:
                cls._clients_by_region[cls._service_name] = {}
            cls._clients_by_region[cls._service_name][aws_region] = client
            return client

        return cls._client

    @classmethod
    def close_connection(cls) -> None:
        """Close the AWS service client connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
        # Close any regional clients for this service only
        service_cache = cls._clients_by_region.get(cls._service_name, {})
        for client in service_cache.values():
            try:
                client.close()
            except Exception:
                pass
        cls._clients_by_region[cls._service_name] = {}


class RDSConnectionManager(BaseConnectionManager):
    """Manages connection to RDS using boto3."""

    _client: Optional[Any] = None
    _service_name = 'rds'
    _env_prefix = 'RDS'


class PIConnectionManager(BaseConnectionManager):
    """Manages connection to PI using boto3."""

    _client: Optional[Any] = None
    _service_name = 'pi'
    _env_prefix = 'PI'


class CloudwatchConnectionManager(BaseConnectionManager):
    """Manages connection to Cloudwatch using boto3."""

    _client: Optional[Any] = None
    _service_name = 'cloudwatch'
    _env_prefix = 'CLOUDWATCH'
