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

"""Tool for retrieving detailed information about RDS DB Clusters (converted from resource)."""

import asyncio
from ...common.connection import RDSConnectionManager
from ...common.decorators.handle_exceptions import handle_exceptions
from ...common.server import mcp
from datetime import datetime
from loguru import logger
from mypy_boto3_rds.type_defs import DBClusterTypeDef
from pydantic import BaseModel, Field
from typing import Dict, List, Optional


DESCRIBE_CLUSTER_DETAIL_TOOL_DESCRIPTION = """Get detailed information about a specific Amazon RDS cluster.

This tool retrieves comprehensive details about a specific RDS database cluster identified by its cluster ID, including configuration, endpoints, backup settings, and maintenance windows.
"""


class ClusterMember(BaseModel):
    """DB cluster member model."""

    instance_id: str = Field(description='The instance identifier of the DB cluster member')
    is_writer: bool = Field(description='Whether the cluster member is a writer instance')
    status: Optional[str] = Field(
        None, description='The status of the DB cluster parameter group for this member'
    )


class Cluster(BaseModel):
    """DB cluster model."""

    cluster_id: str = Field(description='The DB cluster identifier')
    status: str = Field(description='The current status of the DB cluster')
    engine: str = Field(description='The database engine')
    engine_version: Optional[str] = Field(None, description='The version of the database engine')
    endpoint: Optional[str] = Field(
        None, description='The connection endpoint for the primary instance'
    )
    reader_endpoint: Optional[str] = Field(
        None, description='The reader endpoint for the DB cluster'
    )
    multi_az: bool = Field(
        description='Whether the DB cluster has instances in multiple Availability Zones'
    )
    backup_retention: int = Field(description='The retention period for automated backups')
    preferred_backup_window: Optional[str] = Field(
        None, description='The daily time range during which automated backups are created'
    )
    preferred_maintenance_window: Optional[str] = Field(
        None, description='The weekly time range during which system maintenance can occur'
    )
    created_time: Optional[datetime] = Field(
        None, description='The time when the DB cluster was created'
    )
    members: List[ClusterMember] = Field(
        default_factory=list, description='A list of DB cluster members'
    )
    vpc_security_groups: List[Dict[str, str]] = Field(
        default_factory=list, description='A list of VPC security groups the DB cluster belongs to'
    )
    tags: Dict[str, str] = Field(default_factory=dict, description='A list of tags')
    resource_uri: Optional[str] = Field(None, description='The resource URI for this cluster')

    @classmethod
    def from_DBClusterTypeDef(cls, cluster: DBClusterTypeDef) -> 'Cluster':
        """Format cluster information from AWS API response into a detailed structured model."""
        members = []
        for member in cluster.get('DBClusterMembers', []):
            members.append(
                ClusterMember(
                    instance_id=member.get('DBInstanceIdentifier', ''),
                    is_writer=member.get('IsClusterWriter', False),
                    status=member.get('DBClusterParameterGroupStatus'),
                )
            )

        vpc_security_groups = []
        for sg in cluster.get('VpcSecurityGroups', []):
            vpc_security_groups.append(
                {'id': sg.get('VpcSecurityGroupId', ''), 'status': sg.get('Status', '')}
            )

        tags = {}
        if cluster.get('TagList'):
            for tag in cluster.get('TagList', []):
                if 'Key' in tag and 'Value' in tag:
                    tags[tag['Key']] = tag['Value']

        cluster_id = cluster.get('DBClusterIdentifier', '')

        return cls(
            cluster_id=cluster_id,
            status=cluster.get('Status', ''),
            engine=cluster.get('Engine', ''),
            engine_version=cluster.get('EngineVersion'),
            endpoint=cluster.get('Endpoint'),
            reader_endpoint=cluster.get('ReaderEndpoint'),
            multi_az=cluster.get('MultiAZ', False),
            backup_retention=cluster.get('BackupRetentionPeriod', 0),
            preferred_backup_window=cluster.get('PreferredBackupWindow'),
            preferred_maintenance_window=cluster.get('PreferredMaintenanceWindow'),
            created_time=cluster.get('ClusterCreateTime'),
            members=members,
            vpc_security_groups=vpc_security_groups,
            tags=tags,
            resource_uri=f'aws-rds://db-cluster/{cluster_id}',
        )


@mcp.tool(
    name='DescribeDBClusterDetail',
    description=DESCRIBE_CLUSTER_DETAIL_TOOL_DESCRIPTION,
)
@handle_exceptions
async def describe_db_cluster_detail(
    cluster_id: str = Field(
        ..., description='The unique identifier of the RDS DB cluster to retrieve details for'
    ),
    aws_region: str = Field(
        ..., description='AWS region for this call (e.g., us-east-1)'
    ),
) -> Cluster:
    """Retrieve detailed information about a specific RDS cluster.

    Args:
        cluster_id: The unique identifier of the DB cluster.
        aws_region: Region to target for this call (e.g., 'us-east-1').
    """
    logger.info(f'Getting cluster detail (tool) for {cluster_id}')
    rds_client = RDSConnectionManager.get_connection(aws_region=aws_region)
    response = await asyncio.to_thread(
        rds_client.describe_db_clusters, DBClusterIdentifier=cluster_id
    )

    clusters = response.get('DBClusters', [])
    if not clusters:
        raise ValueError(f'Cluster {cluster_id} not found')
    cluster = Cluster.from_DBClusterTypeDef(clusters[0])

    return cluster


