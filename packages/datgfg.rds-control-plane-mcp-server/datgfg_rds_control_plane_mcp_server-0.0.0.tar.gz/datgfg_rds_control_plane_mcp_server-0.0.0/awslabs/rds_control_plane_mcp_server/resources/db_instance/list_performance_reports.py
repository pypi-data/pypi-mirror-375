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

"""Resource for listing available RDS DB Performance Reports."""

import asyncio
from ...common.connection import PIConnectionManager
from ...common.context import RDSContext
from ...common.decorators.handle_exceptions import handle_exceptions
from ...common.server import mcp
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Literal, Optional


LIST_PERFORMANCE_REPORTS_DOCSTRING = """List all available performance reports for a specific Amazon RDS instance.

This resource retrieves Performance Insights analysis reports for a specific RDS database instance, which provide detailed analysis of database performance issues, helping you identify bottlenecks and optimization opportunities.
"""


class PerformanceReportSummary(BaseModel):
    """Performance analysis report information.

    This model represents an Amazon RDS performance analysis report with its metadata,
    including report ID, creation time, time range of the analysis, and status.

    Attributes:
        analysis_report_id: Unique identifier for the performance report.
        create_time: Timestamp when the report was created.
        start_time: Start time of the performance analysis period.
        end_time: End time of the performance analysis period.
        status: Current status of the report (RUNNING, SUCCEEDED, or FAILED).
    """

    # Models the AnalysisReportSummaryTypeDef class which has no required fields
    analysis_report_id: Optional[str] = Field(
        None, description='Unique identifier for the performance report'
    )
    create_time: Optional[datetime] = Field(None, description='Time when the report was created')
    start_time: Optional[datetime] = Field(None, description='Start time of the analysis period')
    end_time: Optional[datetime] = Field(None, description='End time of the analysis period')
    status: Optional[Literal['RUNNING', 'SUCCEEDED', 'FAILED']] = Field(
        None, description='Current status of the report'
    )


class PerformanceReportList(BaseModel):
    """Performance report list model for RDS instances."""

    reports: List[PerformanceReportSummary] = Field(
        default_factory=list, description='List of performance reports for a RDS instance'
    )
    count: int = Field(description='Total number of performance reports')
    resource_uri: str = Field(description='The resource URI for the performance reports')


@mcp.resource(
    uri='aws-rds://db-instance/{dbi_resource_identifier}/performance_report',
    name='ListPerformanceReports',
    mime_type='application/json',
    description=LIST_PERFORMANCE_REPORTS_DOCSTRING,
)
@handle_exceptions
async def list_performance_reports(
    dbi_resource_identifier: str = Field(
        ...,
        description='The resource identifier for the DB instance. This is the DbiResourceId returned by the ListDBInstances resource',
    ),
) -> PerformanceReportList:
    """Retrieve all performance reports for a given DB instance.

    Args:
        dbi_resource_identifier: The DB instance resource identifier

    Returns:
        Performance report list model containing reports and metadata
    """
    if not dbi_resource_identifier:
        raise ValueError('The DB instance resource identifier must be provided')

    pi_client = PIConnectionManager.get_connection()
    reports: List[PerformanceReportSummary] = []
    next_token = None

    while True and len(reports) < RDSContext.max_items():
        request_params = {
            'ServiceType': 'RDS',
            'Identifier': dbi_resource_identifier,
        }

        if next_token:
            request_params['NextToken'] = next_token

        response = await asyncio.to_thread(
            pi_client.list_performance_analysis_reports, **request_params
        )

        if 'AnalysisReports' in response:
            for report in response['AnalysisReports']:
                reports.append(
                    PerformanceReportSummary(
                        analysis_report_id=report.get('AnalysisReportId'),
                        create_time=report.get('CreateTime'),
                        start_time=report.get('StartTime'),
                        end_time=report.get('EndTime'),
                        status=report.get('Status'),
                    )
                )

        if 'NextToken' not in response:
            break

        next_token = response.get('NextToken')

    resource_uri = f'aws-rds://db-instance/{dbi_resource_identifier}/performance_report'

    result = PerformanceReportList(
        reports=reports,
        count=len(reports),
        resource_uri=resource_uri,
    )
    return result
