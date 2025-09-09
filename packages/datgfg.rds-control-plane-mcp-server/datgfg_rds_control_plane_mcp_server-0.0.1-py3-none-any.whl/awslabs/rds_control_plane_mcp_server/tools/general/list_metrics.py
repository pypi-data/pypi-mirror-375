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

"""Tools for listing available CloudWatch metrics for RDS resources (converted from resources)."""

from ...common.connection import CloudwatchConnectionManager
from ...common.decorators.handle_exceptions import handle_exceptions
from ...common.server import mcp
from ...common.utils import handle_paginated_aws_api_call
from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class MetricList(BaseModel):
    """A model for a list of metrics included in the response of the available metrics tools."""

    metrics: List[str] = Field(..., description='List of metrics')
    count: int = Field(..., description='Number of metrics in the list')
    namespace: str = 'AWS/RDS'
    resource_uri: Optional[str] = Field(
        None, description='URI of the resource for which metrics are listed'
    )


def _list_metrics(
    dimension_name: str, dimension_value: str, aws_region: Optional[str]
) -> MetricList:
    cloudwatch_client = CloudwatchConnectionManager.get_connection(
        aws_region=aws_region
    )

    operation_parameters = {
        'Namespace': 'AWS/RDS',
        'Dimensions': [
            {'Name': dimension_name, 'Value': dimension_value},
        ],
    }

    metrics = handle_paginated_aws_api_call(
        client=cloudwatch_client,
        paginator_name='list_metrics',
        operation_parameters=operation_parameters,
        format_function=lambda metric_dict: metric_dict['MetricName'],
        result_key='Metrics',
    )

    return MetricList(
        metrics=metrics,
        count=len(metrics),
        namespace='AWS/RDS',
        resource_uri=None,
    )


@mcp.tool(
    name='ListRDSMetrics',
    description='List available metrics for a RDS resource (db-instance or db-cluster).',
)
@handle_exceptions
def list_rds_metrics_tool(
    resource_type: Literal['db-instance', 'db-cluster'],
    resource_identifier: str,
    aws_region: str,
) -> MetricList:
    """List available CloudWatch metrics for a given RDS resource.

    Args:
        resource_type: Either 'db-instance' or 'db-cluster'.
        resource_identifier: The identifier of the resource.
        aws_region: Region to target for this call (e.g., 'us-east-1').
    """
    dimension_mapping = {
        'db-instance': 'DBInstanceIdentifier',
        'db-cluster': 'DBClusterIdentifier',
    }

    dimension_name = dimension_mapping.get(resource_type)
    if not dimension_name:
        raise ValueError(
            f"Unsupported resource type: {resource_type}. Must be 'db-instance' or 'db-cluster'."
        )

    result = _list_metrics(
        dimension_name=dimension_name,
        dimension_value=resource_identifier,
        aws_region=aws_region,
    )
    result.resource_uri = f'aws-rds://{resource_type}/{resource_identifier}/cloudwatch_metrics'
    return result


