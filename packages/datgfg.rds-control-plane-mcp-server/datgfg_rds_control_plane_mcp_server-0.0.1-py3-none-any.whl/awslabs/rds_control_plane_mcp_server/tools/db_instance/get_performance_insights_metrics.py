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

"""Tool to fetch Performance Insights resource metrics for an RDS instance."""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional

from ...common.connection import PIConnectionManager
from ...common.decorators.handle_exceptions import handle_exceptions
from ...common.server import mcp
from pydantic import BaseModel, Field


GET_PI_METRICS_DESCRIPTION = (
    'Get Performance Insights time-series metrics for an RDS instance by '
    'DbiResourceId. You can specify metric queries (including optional '
    'GroupBy and Limit) and an optional time range and sampling period.'
)


class MetricQueryResult(BaseModel):
    """A single metric time-series returned by Performance Insights."""

    metric: str = Field(
        description='Metric name (e.g., cpuUtilization)'
    )
    unit: Optional[str] = Field(
        None,
        description='Unit of the metric values',
    )
    timestamps: List[datetime] = Field(
        description='List of data point timestamps'
    )
    values: List[float] = Field(
        description='List of data point values'
    )


class ResourceMetricsResponse(BaseModel):
    """Response model for Performance Insights resource metrics."""

    identifier: str = Field(description='DbiResourceId of the RDS instance')
    start_time: datetime = Field(description='Start time of the series')
    end_time: datetime = Field(description='End time of the series')
    period_in_seconds: int = Field(description='Sampling period in seconds')
    results: List[MetricQueryResult] = Field(
        description='List of metric time-series'
    )


def _parse_time(value: Optional[str], default_delta: timedelta) -> datetime:
    if not value:
        return datetime.now() - default_delta
    if value.endswith('Z'):
        value = value.replace('Z', '+00:00')
    return datetime.fromisoformat(value)


def _choose_period(start: datetime, end: datetime) -> int:
    total_seconds = int((end - start).total_seconds())
    if total_seconds <= 3600:
        return 60
    if total_seconds <= 6 * 3600:
        return 300
    return 3600


@mcp.tool(
    name='GetPerformanceInsightsMetrics',
    description=GET_PI_METRICS_DESCRIPTION,
)
@handle_exceptions
async def get_performance_insights_metrics(
    dbi_resource_identifier: str = Field(
        ...,
        description='The DbiResourceId of the RDS instance',
    ),
    metric_name: str = Field(
        ...,
        description='The name of the metric to retrieve. e.g. `db.load.avg`: DB load average',
    ),
    metric_group_by: str = Field(
        ...,
        description='The name of the metric group to retrieve. e.g. `db.sql_tokenized`: group by sql query, `db.host`: group by host, `db.user`: group by user',
    ),
    metric_limit: int = Field(
        ...,
        description='The limit of the metric group to retrieve. e.g. 10, 15, 20',
    ),
    start_time: Optional[str] = Field(
        None,
        description='ISO8601 start time (defaults to now-1h)',
    ),
    end_time: Optional[str] = Field(
        None,
        description='ISO8601 end time (defaults to now)',
    ),
    period_in_seconds: Optional[int] = Field(
        None,
        description='Sampling period in seconds (auto if omitted)',
    ),
    aws_region: str = Field(
        ..., description='AWS region for this call (e.g., us-east-1)'
    ),
) -> dict:
    """Fetch Performance Insights time-series metrics for an RDS instance.

    Args:
        dbi_resource_identifier: The DbiResourceId of the RDS instance.
        metric_name: The name of the metric to retrieve. e.g. `db.load.avg`: DB load average
        metric_group_by: The name of the metric group to retrieve. e.g. `db.sql_tokenized`: group by sql query, `db.host`: group by host, `db.user`: group by user
        metric_limit: The limit of the metric group to retrieve. e.g. 10, 15, 20
        start_time: Optional ISO8601 start time (defaults to now-1h).
        end_time: Optional ISO8601 end time (defaults to now).
        period_in_seconds: Optional sampling period in seconds (auto if omitted).
        aws_region: Region to target for this call (e.g., 'us-east-1').
    """
    end_dt = _parse_time(end_time, timedelta(seconds=0))
    start_dt = _parse_time(start_time, timedelta(hours=1))

    if start_dt >= end_dt:
        raise ValueError('start_time must be before end_time')

    period = period_in_seconds or 300
    # metric_queries are supplied directly by the caller and may already
    # include GroupBy/Limit clauses.

    metric_queries = [
        {
            'Metric': metric_name,
            'GroupBy': {
                'Group': metric_group_by,
                'Limit': metric_limit
            }
        }
    ]
    params = {
        'ServiceType': 'RDS',
        'Identifier': dbi_resource_identifier,
        'StartTime': start_dt,
        'EndTime': end_dt,
        'PeriodInSeconds': period,
        'MetricQueries': metric_queries,
    }

    pi_client = PIConnectionManager.get_connection(aws_region=aws_region)

    # Fetch all pages
    next_token: Optional[str] = None
    merged = {}  # metric -> {unit, timestamps[], values[]}
    while True:
        if next_token:
            params['NextToken'] = next_token
        response = await asyncio.to_thread(
            pi_client.get_resource_metrics, **params
        )

        merged = {**response, 'MetricList': merged.get('MetricList', []) + response.get('MetricList', [])}

        next_token = response.get('NextToken')
        if not next_token:
            break

    return merged

# End of file
# End


