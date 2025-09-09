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

"""Tool for listing available RDS DB Instances (converted from resource)."""

from ...common.connection import RDSConnectionManager
from ...common.decorators.handle_exceptions import handle_exceptions
from ...common.server import mcp
from ...common.utils import handle_paginated_aws_api_call
from loguru import logger
from mypy_boto3_rds.type_defs import DBInstanceTypeDef
from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class InstanceSummary(BaseModel):
    """Simplified DB instance model for list views."""

    instance_id: str = Field(description='The DB instance identifier')
    dbi_resource_id: Optional[str] = Field(
        None, description='The AWS Region-unique, immutable identifier for the DB instance'
    )
    status: str = Field(description='The current status of the DB instance')
    engine: str = Field(description='The database engine')
    engine_version: Optional[str] = Field(None, description='The version of the database engine')
    instance_class: str = Field(
        description='The compute and memory capacity class of the DB instance'
    )
    availability_zone: Optional[str] = Field(
        None, description='The Availability Zone of the DB instance'
    )
    multi_az: bool = Field(description='Whether the DB instance is a Multi-AZ deployment')
    publicly_accessible: bool = Field(description='Whether the DB instance is publicly accessible')
    db_cluster: Optional[str] = Field(
        None, description='The DB cluster identifier, if this is a member of a DB cluster'
    )
    tag_list: Dict[str, str] = Field(default_factory=dict, description='A list of tags')

    @classmethod
    def from_DBInstanceTypeDef(cls, instance: DBInstanceTypeDef) -> 'InstanceSummary':
        """Format instance information into a simplified model for list views."""
        tags = {}
        if instance.get('TagList'):
            for tag in instance.get('TagList', []):
                if 'Key' in tag and 'Value' in tag:
                    tags[tag['Key']] = tag['Value']

        return cls(
            instance_id=instance.get('DBInstanceIdentifier', ''),
            dbi_resource_id=instance.get('DbiResourceId'),
            status=instance.get('DBInstanceStatus', ''),
            engine=instance.get('Engine', ''),
            engine_version=instance.get('EngineVersion', ''),
            instance_class=instance.get('DBInstanceClass', ''),
            availability_zone=instance.get('AvailabilityZone'),
            multi_az=instance.get('MultiAZ', False),
            publicly_accessible=instance.get('PubliclyAccessible', False),
            db_cluster=instance.get('DBClusterIdentifier'),
            tag_list=tags,
        )


class InstanceSummaryList(BaseModel):
    """DB instance list model."""

    instances: List[InstanceSummary] = Field(description='List of DB instances')
    count: int = Field(description='Number of DB instances')
    resource_uri: str = Field(description='The resource URI for instances')


LIST_INSTANCES_TOOL_DESCRIPTION = """List all available Amazon RDS instances in your account.

This tool returns information about all RDS database instances in your AWS account, including identifiers, status, engine details, and configuration.
"""


@mcp.tool(
    name='ListDBInstances',
    description=LIST_INSTANCES_TOOL_DESCRIPTION,
)
@handle_exceptions
async def list_db_instances(
    aws_region: str = Field(
        ..., description='AWS region for this call (e.g., us-east-1)'
    ),
) -> InstanceSummaryList:
    """List all RDS instances in the selected AWS region.

    Args:
        aws_region: Region to target for this call (e.g., 'us-east-1').
    """
    logger.info('Getting instance list (tool)')
    rds_client = RDSConnectionManager.get_connection(aws_region=aws_region)

    instances = handle_paginated_aws_api_call(
        client=rds_client,
        paginator_name='describe_db_instances',
        operation_parameters={},
        format_function=InstanceSummary.from_DBInstanceTypeDef,
        result_key='DBInstances',
    )

    result = InstanceSummaryList(
        instances=instances, count=len(instances), resource_uri='aws-rds://db-instance'
    )

    return result


