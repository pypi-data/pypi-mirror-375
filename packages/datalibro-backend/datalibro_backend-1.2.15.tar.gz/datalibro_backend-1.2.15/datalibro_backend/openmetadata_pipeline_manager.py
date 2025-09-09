#!/usr/bin/env python3
"""
OpenMetadata Pipeline Manager

A Python library for managing OpenMetadata pipelines and lineage tracking with Spark integration.
Supports automatic Pipeline Service and Pipeline entity creation, data lineage management,
and OpenLineage integration for comprehensive data governance.

Author: OpenMetadata Pipeline Manager Team
License: Apache License 2.0
"""

import os
import time
import uuid
import re
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass

try:
    from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
        OpenMetadataConnection,
    )
    from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
        OpenMetadataJWTClientConfig,
    )
    from metadata.ingestion.ometa.ometa_api import OpenMetadata
    from metadata.generated.schema.api.services.createPipelineService import CreatePipelineServiceRequest
    from metadata.generated.schema.entity.services.pipelineService import PipelineServiceType
    from metadata.generated.schema.entity.services.connections.pipeline.customPipelineConnection import CustomPipelineConnection
    from metadata.generated.schema.entity.services.pipelineService import PipelineConnection
    from metadata.generated.schema.api.data.createPipeline import CreatePipelineRequest
    from metadata.generated.schema.entity.data.pipeline import Task
    from metadata.generated.schema.type.entityReference import EntityReference
    from metadata.generated.schema.entity.teams.user import User
    from metadata.generated.schema.api.teams.createUser import CreateUserRequest
    from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
    from metadata.generated.schema.type.entityLineage import EntitiesEdge, LineageDetails
    from metadata.generated.schema.entity.data.table import Table
    from metadata.generated.schema.entity.data.pipeline import Pipeline
    from metadata.generated.schema.entity.services.pipelineService import PipelineService
except ImportError as e:
    raise ImportError(
        f"Required OpenMetadata dependencies not found: {e}. "
        "Please install with: pip install openmetadata-ingestion"
    )


@dataclass
class PipelineConfig:
    """Pipeline configuration class"""
    name: str
    display_name: str
    description: str
    service_name: str
    tasks: Optional[List[Dict[str, Any]]] = None


@dataclass
class OwnerConfig:
    """Owner configuration class"""
    name: str
    email: str
    display_name: Optional[str] = None
    is_admin: bool = False


@dataclass
class OpenLineageConfig:
    """OpenLineage integration configuration"""
    namespace: str = "default-namespace"
    parent_job_name: str = "data-pipeline"
    spark_packages: str = "io.openlineage:openlineage-spark:1.7.0"
    spark_listener: str = "io.openlineage.spark.agent.OpenLineageSparkListener"


class OpenMetadataPipelineManager:
    """
    OpenMetadata Pipeline Manager
    
    A comprehensive manager for OpenMetadata pipelines, services, and lineage tracking
    with built-in Spark OpenLineage integration.
    
    Features:
    - Automatic Pipeline Service creation and management
    - Pipeline entity creation with customizable tasks
    - Data lineage tracking and management
    - User management and ownership assignment
    - Spark OpenLineage integration
    - Comprehensive error handling and logging
    
    Example:
        >>> config = {
        ...     'host': 'http://localhost:8585/api',
        ...     'jwt_token': 'your-jwt-token'
        ... }
        >>> manager = OpenMetadataPipelineManager(config)
        >>> 
        >>> # Create pipeline with lineage
        >>> pipeline_config = PipelineConfig(
        ...     name="data-processing-pipeline",
        ...     display_name="Data Processing Pipeline",
        ...     description="Processes raw data into analytics-ready format",
        ...     service_name="spark-pipeline-service"
        ... )
        >>> 
        >>> owner_config = OwnerConfig(
        ...     name="john.doe",
        ...     email="john.doe@company.com",
        ...     display_name="John Doe"
        ... )
        >>> 
        >>> pipeline = manager.create_complete_pipeline(
        ...     pipeline_config=pipeline_config,
        ...     owner_config=owner_config
        ... )
        >>> 
        >>> # Add data lineage
        >>> manager.add_table_lineage(
        ...     from_table_fqn="source.database.table1",
        ...     to_table_fqn="target.database.table2",
        ...     pipeline_fqn=pipeline.fullyQualifiedName
        ... )
    """
    
    def __init__(
        self,
        openmetadata_config: Dict[str, Any],
        openlineage_config: Optional[OpenLineageConfig] = None,
        enable_logging: bool = True
    ):
        """
        Initialize OpenMetadata Pipeline Manager
        
        Args:
            openmetadata_config: OpenMetadata connection configuration
                Required keys:
                - 'host': OpenMetadata server URL (e.g., 'http://localhost:8585/api')
                - 'jwt_token': JWT authentication token
                Optional keys:
                - 'auth_provider': Authentication provider (default: 'openmetadata')
                - 'verify_ssl': SSL verification (default: True)
            openlineage_config: OpenLineage configuration for Spark integration
            enable_logging: Enable console logging (default: True)
        """
        self.config = openmetadata_config
        self.openlineage_config = openlineage_config or OpenLineageConfig()
        self.enable_logging = enable_logging
        self.metadata = None
        self.run_id = self._generate_run_id()
        self.current_pipeline = None  # 存储当前创建的pipeline
        
        # Initialize OpenMetadata connection
        self._initialize_connection()
    
    def _log(self, message: str, level: str = "INFO"):
        """Internal logging method"""
        if self.enable_logging:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")
    
    def _generate_run_id(self) -> str:
        """Generate unique run ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"pipeline-run-{timestamp}-{str(uuid.uuid4())[:8]}"
    
    def _initialize_connection(self):
        """Initialize OpenMetadata connection"""
        try:
            # Extract configuration with defaults
            host_port = self.config.get('host', 'http://localhost:8585/api')
            jwt_token = self.config.get('jwt_token')
            auth_provider = self.config.get('auth_provider', 'openmetadata')
            
            if not jwt_token:
                raise ValueError("JWT token is required for OpenMetadata connection")
            
            # Create OpenMetadata connection
            server_config = OpenMetadataConnection(
                hostPort=host_port,
                authProvider=auth_provider,
                securityConfig=OpenMetadataJWTClientConfig(jwtToken=jwt_token),
            )
            
            self.metadata = OpenMetadata(server_config)
            self._log(f"✅ OpenMetadata connection established successfully")
            self._log(f"📋 Pipeline Run ID: {self.run_id}")
            
        except Exception as e:
            self._log(f"❌ OpenMetadata connection failed: {e}", "ERROR")
            raise
    
    def _extract_uuid(self, obj: Any) -> str:
        """Extract UUID string from OpenMetadata objects"""
        if hasattr(obj, '__root__'):
            uuid_str = str(obj.__root__)
        else:
            uuid_str = str(obj)
        
        # Handle various UUID formats
        if 'root=UUID(' in uuid_str:
            match = re.search(r"root=UUID\('([^']+)'\)", uuid_str)
            if match:
                return match.group(1)
        elif 'UUID(' in uuid_str:
            match = re.search(r"UUID\('([^']+)'\)", uuid_str)
            if match:
                return match.group(1)
        
        return uuid_str.replace("root=", "").replace("'", "")
    
    def _clean_name_format(self, name_obj: Any) -> str:
        """Clean name format from OpenMetadata objects"""
        name_str = name_obj.__root__ if hasattr(name_obj, '__root__') else str(name_obj)
        
        if 'root=' in str(name_str):
            match = re.search(r"root='([^']+)'", str(name_str))
            if match:
                return match.group(1)
            else:
                return str(name_str).replace("root=", "").replace("'", "")
        
        return str(name_str)
    
    def get_or_create_user(self, owner_config: OwnerConfig) -> Optional[User]:
        """
        Get or create user in OpenMetadata
        
        Args:
            owner_config: User configuration
        
        Returns:
            User object or None if failed
        """
        if not self.metadata:
            self._log("❌ OpenMetadata connection not available", "ERROR")
            return None
        
        try:
            # First, let's diagnose what users exist and their formats
            self._log(f"🔍 Diagnosing user system for: {owner_config.email}")
            
            try:
                users = self.metadata.list_entities(entity=User, limit=100)  # Get more users
                self._log(f"📋 Found {len(users.entities) if hasattr(users, 'entities') and users.entities else 0} total users")
                
                if hasattr(users, 'entities') and users.entities:
                    for i, existing_user in enumerate(users.entities):  # Show all users
                        try:
                            user_name = self._clean_name_format(existing_user.name) if hasattr(existing_user, 'name') else 'NO_NAME'
                            user_email = existing_user.email if hasattr(existing_user, 'email') else 'NO_EMAIL'
                            user_id = self._extract_uuid(existing_user.id) if hasattr(existing_user, 'id') else 'NO_ID'
                            self._log(f"  User {i+1}: name='{user_name}', email='{user_email}', id='{user_id}'")
                            
                            # Check if this is our target user by email (handle root= prefix)
                            if user_email == owner_config.email or user_email == f"root={owner_config.email}":
                                self._log(f"🎯 Found target user by email match!")
                                return existing_user
                            
                            # Also check by name match (including partial matches)
                            if (user_name == owner_config.name or 
                                user_name == owner_config.display_name or
                                user_name.startswith(owner_config.name) or
                                owner_config.name in user_name):
                                self._log(f"🎯 Found target user by name match!")
                                return existing_user
                        except Exception as debug_error:
                            self._log(f"  User {i+1}: Could not parse user info: {debug_error}")
                
                # If we didn't find by email, try by name
                for existing_user in users.entities:
                    try:
                        if hasattr(existing_user, 'name'):
                            user_name = self._clean_name_format(existing_user.name)
                            if user_name == owner_config.name:
                                self._log(f"🎯 Found target user by name match!")
                                return existing_user
                    except Exception as name_check_error:
                        continue
                        
            except Exception as list_error:
                self._log(f"⚠️ User listing failed: {list_error}", "WARNING")
            
            # If we still haven't found the user, try direct lookup
            try:
                user = self.metadata.get_by_name(entity=User, fqn=owner_config.name)
                if user:
                    self._log(f"🎯 Found user by direct lookup: {user}")
                    return user
            except Exception as direct_error:
                self._log(f"⚠️ Direct user lookup failed: {direct_error}", "WARNING")
                
            self._log(f"❌ Could not find user {owner_config.name} ({owner_config.email})", "ERROR")
            return None
            
        except Exception as e:
            self._log(f"❌ User retrieval failed: {e}", "ERROR")
            return None
    
    def create_pipeline_service(self, service_name: str, service_description: Optional[str] = None) -> Optional[str]:
        """
        Create or get Pipeline Service
        
        Args:
            service_name: Name of the pipeline service
            service_description: Optional description
        
        Returns:
            Service ID or None if failed
        """
        if not self.metadata:
            self._log("❌ OpenMetadata connection not available", "ERROR")
            return None
        
        try:
            # Try to get existing service first
            try:
                existing_service = self.metadata.get_by_name(entity=PipelineService, fqn=service_name)
                service_id = self._extract_uuid(existing_service.id)
                self._log(f"🔧 Found existing Pipeline Service: {self._clean_name_format(existing_service.name)}")
                return service_id
            except:
                pass
            
            # Create new service
            description = service_description or f"Pipeline service for {service_name}"
            
            # Create proper PipelineConnection structure
            custom_config = CustomPipelineConnection(
                type="CustomPipeline",
                sourcePythonClass=f"{service_name.replace('-', '_')}_service"
            )
            
            pipeline_connection = PipelineConnection(config=custom_config)
            
            service_request = CreatePipelineServiceRequest(
                name=service_name,
                displayName=service_name.replace('-', ' ').title(),
                description=description,
                serviceType=PipelineServiceType.CustomPipeline,
                connection=pipeline_connection
            )
            
            service = self.metadata.create_or_update(service_request)
            service_id = self._extract_uuid(service.id)
            
            self._log(f"🔧 Created Pipeline Service: {self._clean_name_format(service.name)} (ID: {service_id})")
            return service_id
            
        except Exception as e:
            self._log(f"❌ Pipeline Service creation failed: {e}", "ERROR")
            return None
    
    def create_pipeline_entity(
        self,
        pipeline_config: PipelineConfig,
        owner_config: Optional[OwnerConfig] = None
    ) -> Optional[Pipeline]:
        """
        Create Pipeline entity
        
        Args:
            pipeline_config: Pipeline configuration
            owner_config: Optional owner configuration
        
        Returns:
            Pipeline object or None if failed
        """
        if not self.metadata:
            self._log("❌ OpenMetadata connection not available", "ERROR")
            return None
        
        # First check if pipeline already exists
        try:
            service_fqn = pipeline_config.service_name
            pipeline_fqn = f"{service_fqn}.{pipeline_config.name}"
            existing_pipeline = self.metadata.get_by_name(entity=Pipeline, fqn=pipeline_fqn)
            if existing_pipeline:
                self._log(f"📋 Found existing Pipeline: {self._clean_name_format(existing_pipeline.name)}")
                self.current_pipeline = existing_pipeline
                
                # Process owner assignment for existing Pipeline if provided
                if owner_config:
                    self._log(f"🔍 Processing owner for existing Pipeline: {owner_config.name} ({owner_config.email})")
                    owner_user = self.get_or_create_user(owner_config)
                    if owner_user:
                        owner_id = self._extract_uuid(owner_user.id) if hasattr(owner_user, 'id') else str(owner_user.id)
                        # Try to update existing pipeline with new owner - recreate it with proper owner
                        try:
                            from metadata.generated.schema.api.data.createPipeline import CreatePipelineRequest
                            
                            owner_ref = EntityReference(id=owner_id, type="user")
                            
                            # Extract service name from service EntityReference
                            service_name = None
                            if hasattr(existing_pipeline.service, 'name'):
                                service_name = existing_pipeline.service.name
                            elif hasattr(existing_pipeline, 'service'):
                                # If service is an EntityReference, get the name from it
                                try:
                                    service_entity = self.metadata.get_by_name(entity=PipelineService, fqn=existing_pipeline.service.name)
                                    service_name = service_entity.name
                                except:
                                    # Fallback - extract from FQN
                                    service_name = str(existing_pipeline.service.name) if hasattr(existing_pipeline.service, 'name') else pipeline_config.service_name
                            
                            if not service_name:
                                service_name = pipeline_config.service_name
                            
                            self._log(f"🔄 Recreating Pipeline with owner. Service: {service_name}")
                            
                            # Extract and convert existing tasks properly
                            tasks_list = []
                            if hasattr(existing_pipeline, 'tasks') and existing_pipeline.tasks:
                                self._log(f"📋 Found {len(existing_pipeline.tasks)} existing tasks to preserve")
                                for task in existing_pipeline.tasks:
                                    # Convert task to proper format
                                    task_dict = {
                                        'name': task.name if hasattr(task, 'name') else 'default-task',
                                        'taskType': task.taskType if hasattr(task, 'taskType') else 'TRANSFORM',
                                        'description': task.description if hasattr(task, 'description') else '',
                                        'displayName': task.displayName if hasattr(task, 'displayName') else (task.name if hasattr(task, 'name') else 'Default Task')
                                    }
                                    tasks_list.append(task_dict)
                            else:
                                self._log(f"📋 No existing tasks found, creating default tasks")
                                # Create default tasks for data pipeline
                                tasks_list = [
                                    {
                                        'name': 'data-extraction',
                                        'taskType': 'TRANSFORM',
                                        'description': '从MySQL dl_cloud数据库提取设备档案数据',
                                        'displayName': 'Data Extraction'
                                    },
                                    {
                                        'name': 'data-transformation',
                                        'taskType': 'TRANSFORM', 
                                        'description': '数据清洗和转换处理',
                                        'displayName': 'Data Transformation'
                                    },
                                    {
                                        'name': 'data-loading',
                                        'taskType': 'TRANSFORM',
                                        'description': '将处理后的数据加载到TiDB ods_device_profile_detail_di表',
                                        'displayName': 'Data Loading'
                                    }
                                ]
                            
                            # Create Task objects
                            from metadata.generated.schema.entity.data.pipeline import Task
                            task_objects = []
                            for task_config in tasks_list:
                                task = Task(
                                    name=task_config['name'],
                                    taskType=task_config['taskType'],
                                    description=task_config.get('description', ''),
                                    displayName=task_config.get('displayName', task_config['name'])
                                )
                                task_objects.append(task)
                            
                            # Create new Pipeline request with owner and preserved tasks
                            create_request = CreatePipelineRequest(
                                name=existing_pipeline.name,
                                displayName=existing_pipeline.displayName or existing_pipeline.name,
                                description=existing_pipeline.description or f"Pipeline managed by {owner_user.name}",
                                service=service_name,  # Use service name as string, not EntityReference
                                tasks=task_objects,  # Use properly formatted Task objects
                                owners=[owner_ref]
                            )
                            
                            updated_pipeline = self.metadata.create_or_update(create_request)
                            self._log(f"✅ Recreated Pipeline with owner: {owner_user.name} ({owner_id})")
                            self.current_pipeline = updated_pipeline
                            return updated_pipeline
                            
                        except Exception as update_error:
                            self._log(f"⚠️ Could not recreate Pipeline with owner: {update_error}", "WARNING")
                            # Fallback - continue with existing pipeline
                            self._log(f"🔄 Continuing with existing Pipeline without persistent owner")
                            self.current_pipeline = existing_pipeline
                    else:
                        self._log("❌ Owner user is None, existing Pipeline owner unchanged")
                
                return existing_pipeline
        except Exception as check_error:
            self._log(f"📝 Pipeline does not exist, will create new one: {check_error}")
        
        try:
            # Create or get pipeline service
            service_id = self.create_pipeline_service(
                service_name=pipeline_config.service_name,
                service_description=f"Service for {pipeline_config.display_name}"
            )
            
            if not service_id:
                self._log("❌ Failed to create Pipeline Service", "ERROR")
                return None
            
            # Verify service exists and get clean name
            try:
                pipeline_service = self.metadata.get_by_name(entity=PipelineService, fqn=pipeline_config.service_name)
                service_reference = self._clean_name_format(pipeline_service.name)
                self._log(f"✅ Verified Pipeline Service: {service_reference}")
            except Exception as e:
                self._log(f"❌ Service verification failed: {e}", "ERROR")
                return None
            
            # Handle owner - only for new pipelines
            owners = []
            if owner_config:
                self._log(f"🔍 Setting up owner for new Pipeline: {owner_config.name} ({owner_config.email})")
                # Use proper user retrieval method with diagnostic logging
                owner_user = self.get_or_create_user(owner_config)
                if owner_user:
                    owner_id = self._extract_uuid(owner_user.id) if hasattr(owner_user, 'id') else str(owner_user.id)
                    owners.append(EntityReference(id=owner_id, type="user"))
                    self._log(f"✅ Added Pipeline owner: {owner_user.name} ({owner_id})")
                else:
                    self._log("❌ Owner user is None, no owner will be assigned")
            else:
                self._log("📝 No owner config provided")
            
            # Create tasks
            from metadata.generated.schema.entity.data.pipeline import Task
            tasks = []
            if pipeline_config.tasks:
                for task_config in pipeline_config.tasks:
                    task = Task(
                        name=task_config.get('name', 'default-task'),
                        displayName=task_config.get('display_name', task_config.get('name', 'Default Task')),
                        description=task_config.get('description', ''),
                        taskType=task_config.get('task_type', 'TRANSFORM'),
                        owners=owners if owners else None
                    )
                    tasks.append(task)
            else:
                # Default tasks
                default_tasks = [
                    {
                        'name': 'extract-data',
                        'display_name': 'Extract Data',
                        'description': 'Extract data from source systems',
                        'task_type': 'EXTRACT'
                    },
                    {
                        'name': 'transform-data',
                        'display_name': 'Transform Data',
                        'description': 'Transform and process data',
                        'task_type': 'TRANSFORM'
                    },
                    {
                        'name': 'load-data',
                        'display_name': 'Load Data',
                        'description': 'Load data to target systems',
                        'task_type': 'LOAD'
                    }
                ]
                
                for task_config in default_tasks:
                    task = Task(
                        name=task_config['name'],
                        displayName=task_config['display_name'],
                        description=task_config['description'],
                        taskType=task_config['task_type'],
                        owners=owners if owners else None
                    )
                    tasks.append(task)
            
            # Create pipeline request
            from metadata.generated.schema.api.data.createPipeline import CreatePipelineRequest
            pipeline_request = CreatePipelineRequest(
                name=pipeline_config.name,
                displayName=pipeline_config.display_name,
                description=pipeline_config.description,
                service=service_reference,
                owners=owners,
                tasks=tasks
            )
            
            # Create pipeline
            pipeline = self.metadata.create_or_update(pipeline_request)
            self._log(f"🚀 Pipeline created successfully: {self._clean_name_format(pipeline.name)}")
            
            # 保存当前创建的pipeline以供血缘关系使用
            self.current_pipeline = pipeline
            
            # Display owner info
            if hasattr(pipeline, 'owners') and pipeline.owners:
                try:
                    owner_count = len(pipeline.owners) if hasattr(pipeline.owners, '__len__') else len(list(pipeline.owners))
                    self._log(f"👥 Pipeline Owners: {owner_count} assigned")
                except:
                    self._log("👥 Pipeline Owners: assigned (count unknown)")
            else:
                self._log("👥 Pipeline has no owners assigned")
            
            return pipeline
            
        except Exception as e:
            self._log(f"❌ Pipeline creation failed: {e}", "ERROR")
            return None
    
    def add_table_lineage(self, from_table_fqn, to_table_fqn, description="", pipeline_fqn=None, auto_associate_pipeline=True):
        """添加表血缘关系 - 包含Pipeline关联
        
        Args:
            from_table_fqn: 源表FQN
            to_table_fqn: 目标表FQN  
            description: 血缘关系描述
            pipeline_fqn: 指定的Pipeline FQN
            auto_associate_pipeline: 是否自动关联最近创建的pipeline
        """
        if not self.metadata:
            self._log("❌ OpenMetadata connection not available", "ERROR")
            return False
            
        try:
            # 获取源表和目标表
            from metadata.generated.schema.entity.data.table import Table
            from metadata.generated.schema.type.entityLineage import EntitiesEdge, LineageDetails
            
            # 获取源表
            try:
                from_table = self.metadata.get_by_name(entity=Table, fqn=from_table_fqn)
            except Exception as e:
                self._log(f"❌ 源表不存在: {from_table_fqn} - {e}", "ERROR")
                return False
            
            # 获取目标表
            try:
                to_table = self.metadata.get_by_name(entity=Table, fqn=to_table_fqn)
            except Exception as e:
                self._log(f"❌ 目标表不存在: {to_table_fqn} - {e}", "ERROR")
                return False
            
            from_table_id = self._extract_uuid(from_table.id)
            to_table_id = self._extract_uuid(to_table.id)
            
            # 获取pipeline实体用于血缘关系（优先使用pipeline_fqn，否则尝试获取当前pipeline）
            pipeline_ref = None
            if pipeline_fqn:
                # 如果提供了pipeline_fqn，使用指定的Pipeline
                try:
                    pipeline_entity = self.metadata.get_by_name(entity=Pipeline, fqn=pipeline_fqn)
                    pipeline_id = self._extract_uuid(pipeline_entity.id)
                    pipeline_ref = EntityReference(id=pipeline_id, type="pipeline")
                    self._log(f"🔗 将指定Pipeline关联到血缘关系: {pipeline_id}")
                except Exception as pe:
                    self._log(f"⚠️ 指定Pipeline关联失败: {pe}", "WARNING")
            elif auto_associate_pipeline and self.current_pipeline:
                # 如果没有提供pipeline_fqn但启用了自动关联，使用当前创建的pipeline
                try:
                    pipeline_id = self._extract_uuid(self.current_pipeline.id)
                    pipeline_ref = EntityReference(id=pipeline_id, type="pipeline")
                    self._log(f"🔗 自动关联当前Pipeline到血缘关系: {pipeline_id}")
                except Exception as pe:
                    self._log(f"⚠️ 自动Pipeline关联失败: {pe}", "WARNING")
            else:
                self._log("🔗 未关联Pipeline，创建简单血缘关系")
            
            # 创建血缘关系 - 包含Pipeline上下文（如果可用）
            edge = EntitiesEdge(
                fromEntity=EntityReference(id=from_table_id, type="table"),
                toEntity=EntityReference(id=to_table_id, type="table"),
                lineageDetails=LineageDetails(
                    description=description or f"数据血缘: {from_table_fqn} → {to_table_fqn}",
                    pipeline=pipeline_ref
                )
            )
            
            lineage_request = AddLineageRequest(edge=edge)
            self.metadata.add_lineage(lineage_request)
            
            if pipeline_ref:
                self._log(f"✅ 血缘关系添加成功(含Pipeline): {from_table_fqn} → {to_table_fqn}")
            else:
                self._log(f"✅ 血缘关系添加成功: {from_table_fqn} → {to_table_fqn}")
            return True
            
        except Exception as e:
            self._log(f"❌ 添加血缘关系失败: {e}", "ERROR")
            return False
    
    def get_pipeline_info(self, pipeline_name: str) -> Optional[Dict[str, Any]]:
        """
        Get pipeline information
        
        Args:
            pipeline_name: Pipeline name
        
        Returns:
            Pipeline information dictionary or None
        """
        if not self.metadata:
            self._log("❌ OpenMetadata connection not available", "ERROR")
            return None
        
        try:
            pipeline = self.metadata.get_by_name(entity=Pipeline, fqn=pipeline_name)
            
            info = {
                'name': self._clean_name_format(pipeline.name),
                'id': self._extract_uuid(pipeline.id),
                'description': self._clean_name_format(pipeline.description) if pipeline.description else None,
                'status': pipeline.pipelineStatus,
                'service': self._clean_name_format(pipeline.service.name) if pipeline.service else None,
                'owners': [
                    {
                        'id': self._extract_uuid(owner.id),
                        'name': self._clean_name_format(owner.name),
                        'type': owner.type
                    }
                    for owner in (list(pipeline.owners) if pipeline.owners else [])
                    if hasattr(owner, 'id') and hasattr(owner, 'name') and hasattr(owner, 'type')
                ],
                'tasks': [
                    {
                        'name': self._clean_name_format(task.name),
                        'type': task.taskType,
                        'description': task.description
                    }
                    for task in (list(pipeline.tasks) if pipeline.tasks else [])
                ]
            }
            
            self._log(f"📋 Pipeline info retrieved: {info['name']}")
            return info
            
        except Exception as e:
            self._log(f"❌ Failed to get pipeline info: {e}", "ERROR")
            return None
    
    def get_pipeline(self, pipeline_name, service_name=""):
        """获取已存在的Pipeline"""
        if not self.metadata:
            self._log("❌ OpenMetadata connection not available", "ERROR")
            return None
            
        try:
            # 如果没有提供service_name，尝试从pipeline_name构建FQN
            if not service_name:
                # 尝试直接使用pipeline_name作为FQN
                fqn = pipeline_name
            else:
                fqn = f"{service_name}.{pipeline_name}"
            
            # 通过名称获取Pipeline
            pipeline = self.metadata.get_by_name(entity=Pipeline, fqn=fqn)
            
            self._log(f"📋 获取到Pipeline: {self._clean_name_format(pipeline.name)}")
            self._log(f"Pipeline ID: {self._extract_uuid(pipeline.id)}")
            self._log(f"Pipeline描述: {pipeline.description or 'N/A'}")
            
            # 显示Pipeline的任务
            if hasattr(pipeline, 'tasks') and pipeline.tasks:
                self._log("Pipeline任务:")
                for i, task in enumerate(pipeline.tasks, 1):
                    self._log(f"  {i}. {self._clean_name_format(task.name)} ({task.taskType}): {task.description}")
            
            return pipeline
        except Exception as e:
            self._log(f"❌ 获取Pipeline失败: {e}", "ERROR")
            return None

    def get_pipeline_lineage(self, pipeline_name, service_name=""):
        """获取Pipeline的血缘关系"""
        if not self.metadata:
            self._log("❌ OpenMetadata connection not available", "ERROR")
            return None
            
        try:
            pipeline = self.get_pipeline(pipeline_name, service_name)
            if not pipeline:
                return None
                
            # 构建FQN
            if not service_name:
                fqn = pipeline_name
            else:
                fqn = f"{service_name}.{pipeline_name}"
                
            # 获取血缘关系
            lineage = self.metadata.get_lineage_by_name(
                entity=Pipeline,
                fqn=fqn,
                up_depth=3,
                down_depth=3
            )
            
            self._log("📊 Pipeline血缘关系:")
            if lineage and lineage.get('edges'):
                for edge in lineage['edges']:
                    from_entity = edge.get('fromEntity', {})
                    to_entity = edge.get('toEntity', {})
                    self._log(f"  {from_entity.get('name', 'Unknown')} -> {to_entity.get('name', 'Unknown')}")
            else:
                self._log("  未找到血缘关系")
                
            return lineage
        except Exception as e:
            self._log(f"❌ 获取Pipeline血缘关系失败: {e}", "ERROR")
            return None

    def track_pipeline_execution(self, status="success", start_time=None, end_time=None, metrics=None):
        """跟踪管道执行状态"""
        if not self.metadata:
            return
            
        try:
            execution_info = {
                "run_id": self.run_id,
                "status": status,
                "start_time": start_time or datetime.now(),
                "end_time": end_time or datetime.now(),
                "metrics": metrics or {}
            }
            self._log(f"📈 管道执行跟踪: {execution_info}")
        except Exception as e:
            self._log(f"❌ 跟踪管道执行失败: {e}", "ERROR")

    def configure_spark_openlineage(self, spark_session_or_builder) -> Any:
        """
        Configure Spark session with OpenLineage integration
        
        Args:
            spark_session_or_builder: SparkSession.builder object or existing SparkSession
        
        Returns:
            Configured SparkSession.builder or SparkSession
        """
        try:
            # Extract OpenMetadata host for OpenLineage
            om_host = self.config.get('host', 'http://localhost:8585')
            if om_host.endswith('/api'):
                om_host = om_host[:-4]  # Remove /api suffix
            
            # Check if it's a SparkSession or SparkSession.builder
            if hasattr(spark_session_or_builder, 'sparkContext'):
                # It's an existing SparkSession
                self._log("⚡ Configuring existing SparkSession with OpenLineage")
                spark_context = spark_session_or_builder.sparkContext
                
                # Configure runtime properties
                spark_context.setLocalProperty("spark.openlineage.namespace", self.openlineage_config.namespace)
                spark_context.setLocalProperty("spark.openlineage.parentJobName", self.openlineage_config.parent_job_name)
                
                # Log configuration (runtime configuration is limited for existing sessions)
                self._log("⚡ Spark session configured with OpenLineage integration")
                self._log("ℹ️ Note: Some OpenLineage configurations require restart for existing sessions")
                return spark_session_or_builder
                
            else:
                # It's a SparkSession.builder
                self._log("⚡ Configuring SparkSession.builder with OpenLineage")
                configured_builder = spark_session_or_builder \
                    .config("spark.openlineage.namespace", self.openlineage_config.namespace) \
                    .config("spark.openlineage.parentJobName", self.openlineage_config.parent_job_name) \
                    .config("spark.jars.packages", self.openlineage_config.spark_packages) \
                    .config("spark.extraListeners", self.openlineage_config.spark_listener) \
                    .config("spark.openlineage.transport.type", "http") \
                    .config("spark.openlineage.transport.url", f"{om_host}/api/v1/lineage") \
                    .config("spark.openlineage.transport.auth.type", "api_key") \
                    .config("spark.openlineage.transport.auth.apiKey", self.config.get('jwt_token', ''))
                
                self._log("⚡ Spark session configured with OpenLineage integration")
                return configured_builder
            
        except Exception as e:
            self._log(f"⚠️ Spark OpenLineage configuration warning: {e}", "WARNING")
            return spark_session_or_builder
    
    def create_complete_pipeline(
        self,
        pipeline_config: PipelineConfig,
        owner_config: Optional[OwnerConfig] = None,
        lineage_mappings: Optional[List[Dict[str, str]]] = None
    ) -> Optional[Pipeline]:
        """
        Create a complete pipeline with service, entity, and optional lineage
        
        Args:
            pipeline_config: Pipeline configuration
            owner_config: Optional owner configuration
            lineage_mappings: Optional list of lineage mappings
                Each mapping should have 'from_table_fqn' and 'to_table_fqn' keys
        
        Returns:
            Pipeline object or None if failed
        """
        self._log("🚀 Creating complete pipeline setup...")
        
        # Create pipeline entity
        pipeline = self.create_pipeline_entity(pipeline_config, owner_config)
        if not pipeline:
            return None
        
        # Add lineage if provided
        if lineage_mappings:
            self._log(f"🔗 Adding {len(lineage_mappings)} lineage relationships...")
            # Use pipeline fullyQualifiedName for proper lineage association
            pipeline_fqn = self._clean_name_format(pipeline.fullyQualifiedName) if hasattr(pipeline, 'fullyQualifiedName') else self._clean_name_format(pipeline.name)
            
            for mapping in lineage_mappings:
                from_table = mapping.get('from_table_fqn')
                to_table = mapping.get('to_table_fqn')
                description = mapping.get('description')
                
                if from_table and to_table:
                    self.add_table_lineage(
                        from_table_fqn=from_table,
                        to_table_fqn=to_table,
                        description=description or f"数据血缘: {from_table} → {to_table}",
                        pipeline_fqn=pipeline_fqn,
                        auto_associate_pipeline=True  # 启用自动关联
                    )
        
        self._log("✅ Complete pipeline setup finished successfully!")
        return pipeline


# Convenience functions for quick usage
def create_pipeline_manager(
    openmetadata_host: str,
    jwt_token: str,
    **kwargs
) -> OpenMetadataPipelineManager:
    """
    Convenience function to create pipeline manager
    
    Args:
        openmetadata_host: OpenMetadata server URL
        jwt_token: JWT authentication token
        **kwargs: Additional configuration options
    
    Returns:
        OpenMetadataPipelineManager instance
    """
    config = {
        'host': openmetadata_host,
        'jwt_token': jwt_token,
        **kwargs
    }
    return OpenMetadataPipelineManager(config)


def quick_pipeline_setup(
    openmetadata_host: str,
    jwt_token: str,
    pipeline_name: str,
    pipeline_description: str,
    owner_email: str,
    owner_name: Optional[str] = None,
    lineage_mappings: Optional[List[Dict[str, str]]] = None
) -> Optional[Pipeline]:
    """
    Quick pipeline setup with minimal configuration
    
    Args:
        openmetadata_host: OpenMetadata server URL
        jwt_token: JWT authentication token
        pipeline_name: Pipeline name
        pipeline_description: Pipeline description
        owner_email: Owner email address
        owner_name: Optional owner name (derived from email if not provided)
        lineage_mappings: Optional lineage mappings
    
    Returns:
        Pipeline object or None if failed
    """
    # Create manager
    manager = create_pipeline_manager(openmetadata_host, jwt_token)
    
    # Configure pipeline
    service_name = f"{pipeline_name}-service"
    pipeline_config = PipelineConfig(
        name=pipeline_name,
        display_name=pipeline_name.replace('-', ' ').replace('_', ' ').title(),
        description=pipeline_description,
        service_name=service_name
    )
    
    # Configure owner
    if not owner_name:
        owner_name = owner_email.split('@')[0]
    
    owner_config = OwnerConfig(
        name=owner_name,
        email=owner_email,
        display_name=owner_name.replace('.', ' ').replace('_', ' ').title()
    )
    
    # Create pipeline
    return manager.create_complete_pipeline(
        pipeline_config=pipeline_config,
        owner_config=owner_config,
        lineage_mappings=lineage_mappings
    )


if __name__ == "__main__":
    # Example usage
    print("OpenMetadata Pipeline Manager")
    print("=" * 50)
    
    # Example configuration (replace with your values)
    example_config = {
        'host': 'http://localhost:8585/api',
        'jwt_token': 'your-jwt-token-here'
    }
    
    print("Example usage:")
    print("""
# Basic usage
from openmetadata_pipeline_manager import create_pipeline_manager, PipelineConfig, OwnerConfig

# Create manager
manager = create_pipeline_manager(
    openmetadata_host='http://localhost:8585/api',
    jwt_token='your-jwt-token'
)

# Configure pipeline
pipeline_config = PipelineConfig(
    name="data-processing-pipeline",
    display_name="Data Processing Pipeline", 
    description="Processes raw data into analytics format",
    service_name="spark-pipeline-service"
)

# Configure owner
owner_config = OwnerConfig(
    name="john.doe",
    email="john.doe@company.com",
    display_name="John Doe"
)

# Create pipeline
pipeline = manager.create_complete_pipeline(
    pipeline_config=pipeline_config,
    owner_config=owner_config
)

# Add lineage
manager.add_table_lineage(
    from_table_fqn="source.db.table1",
    to_table_fqn="target.db.table2",
    description="ETL process lineage"
)

# Configure Spark with OpenLineage
from pyspark.sql import SparkSession
spark = manager.configure_spark_openlineage(SparkSession.builder).getOrCreate()
""")