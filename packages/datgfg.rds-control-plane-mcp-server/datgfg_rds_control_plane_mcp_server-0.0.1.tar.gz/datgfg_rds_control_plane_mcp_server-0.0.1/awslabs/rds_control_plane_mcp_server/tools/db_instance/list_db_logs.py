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

"""Tool for listing available RDS DB Log Files (converted from resource)."""

from ...common.connection import RDSConnectionManager
from ...common.decorators.handle_exceptions import handle_exceptions
from ...common.server import mcp
from ...common.utils import handle_paginated_aws_api_call
from datetime import datetime
from mypy_boto3_rds.type_defs import DescribeDBLogFilesResponseTypeDef
from pydantic import BaseModel, Field
from typing import List, Optional


class DBLogFileSummary(BaseModel):
    """Database log file information."""

    log_file_name: str = Field(description='Name of the log file')
    last_written: datetime = Field(
        description='A POSIX timestamp when the last log entry was written.'
    )
    size: int = Field(description='Size of the log file in bytes', ge=0)

    @classmethod
    def from_DescribeDBLogFilesDetailsTypeDef(
        cls, log_file: DescribeDBLogFilesResponseTypeDef
    ) -> 'DBLogFileSummary':
        return cls(
            log_file_name=log_file.get('LogFileName', ''),
            last_written=datetime.fromtimestamp(log_file.get('LastWritten', 0) / 1000),
            size=log_file.get('Size', 0),
        )


class DBLogFileList(BaseModel):
    """DB cluster list model."""

    log_files: List[DBLogFileSummary] = Field(
        default_factory=list, description='List of DB log files'
    )
    count: int = Field(
        description='Total number of non-empty log files for the DB instance in Amazon RDS'
    )
    resource_uri: str = Field(description='The resource URI for the DB log files')


LIST_DB_LOG_FILES_TOOL_DESCRIPTION = """List all available NON-EMPTY log files for a specific Amazon RDS instance."""


@mcp.tool(
    name='ListDBLogFiles',
    description=LIST_DB_LOG_FILES_TOOL_DESCRIPTION,
)
@handle_exceptions
async def list_rds_db_log_files(
    db_instance_identifier: str = Field(..., description='The identifier for the DB instance'),
    aws_region: str = Field(
        ..., description='AWS region for this call (e.g., us-east-1)'
    ),
) -> DBLogFileList:
    """List all non-empty log files for the database.

    Args:
        db_instance_identifier: The DB instance identifier to query logs for.
        aws_region: Region to target for this call (e.g., 'us-east-1').
    """
    rds_client = RDSConnectionManager.get_connection(aws_region=aws_region)

    params = {
        'DBInstanceIdentifier': db_instance_identifier,
        'FileSize': 1,
    }

    log_files = handle_paginated_aws_api_call(
        client=rds_client,
        paginator_name='describe_db_log_files',
        operation_parameters=params,
        format_function=DBLogFileSummary.from_DescribeDBLogFilesDetailsTypeDef,
        result_key='DescribeDBLogFiles',
    )

    result = DBLogFileList(
        log_files=log_files,
        count=len(log_files),
        resource_uri='aws-rds://db-instance/{db_instance_identifier}/log',
    )

    return result


