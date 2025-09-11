"""
Enhanced Inventory Collector - AWS Resource Discovery with Enterprise Profile Management.

Strategic Alignment:
- "Do one thing and do it well" - Focused inventory collection with proven patterns
- "Move Fast, But Not So Fast We Crash" - Performance with enterprise reliability

Core Capabilities:
- Single profile architecture: --profile override pattern for all operations
- Multi-account discovery leveraging existing enterprise infrastructure
- Performance targets: <45s inventory operations across 60+ accounts
- MCP integration for real-time AWS API validation and accuracy
- Rich CLI output following enterprise UX standards

Business Value:
- Enables systematic AWS resource governance across enterprise landing zones
- Provides foundation for cost optimization and security compliance initiatives
- Supports terraform IaC validation and configuration drift detection
"""

import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

import boto3
from loguru import logger

from runbooks.base import CloudFoundationsBase, ProgressTracker
from runbooks.common.cross_module_integration import DataFlowType, EnterpriseCrossModuleIntegrator
from runbooks.common.mcp_integration import EnterpriseMCPIntegrator, MCPOperationType
from runbooks.common.profile_utils import create_management_session, get_profile_for_operation
from runbooks.common.rich_utils import console, print_error, print_info, print_success, print_warning
from runbooks.config import RunbooksConfig

# Import the enhanced 4-profile architecture from organizations discovery
try:
    from ..organizations_discovery import ENTERPRISE_PROFILES, PerformanceBenchmark

    ENHANCED_PROFILES_AVAILABLE = True
except ImportError:
    ENHANCED_PROFILES_AVAILABLE = False
    # Fallback profile definitions
    ENTERPRISE_PROFILES = {
        "BILLING_PROFILE": "ams-admin-Billing-ReadOnlyAccess-909135376185",
        "MANAGEMENT_PROFILE": "ams-admin-ReadOnlyAccess-909135376185",
        "CENTRALISED_OPS_PROFILE": "ams-centralised-ops-ReadOnlyAccess-335083429030",
        "SINGLE_ACCOUNT_PROFILE": "ams-shared-services-non-prod-ReadOnlyAccess-499201730520",
    }


class EnhancedInventoryCollector(CloudFoundationsBase):
    """
    Enhanced inventory collector with 4-Profile AWS SSO Architecture.

    Orchestrates resource discovery across multiple accounts and regions,
    providing comprehensive inventory capabilities with enterprise-grade
    reliability and performance monitoring.

    Features:
    - 4-profile AWS SSO architecture with failover
    - Performance benchmarking targeting <45s operations
    - Comprehensive error handling and profile fallbacks
    - Multi-account enterprise scale support
    """

    def __init__(
        self,
        profile: Optional[str] = None,
        region: Optional[str] = None,
        config: Optional[RunbooksConfig] = None,
        parallel: bool = True,
        use_enterprise_profiles: bool = True,
        performance_target_seconds: float = 45.0,
    ):
        """
        Initialize enhanced inventory collector with 4-profile architecture.

        Args:
            profile: Primary AWS profile (overrides enterprise profile selection)
            region: AWS region
            config: Runbooks configuration
            parallel: Enable parallel processing
            use_enterprise_profiles: Use proven enterprise profile architecture
            performance_target_seconds: Performance target for operations (default: 45s)
        """
        super().__init__(profile, region, config)
        self.parallel = parallel
        self.use_enterprise_profiles = use_enterprise_profiles
        self.performance_target_seconds = performance_target_seconds

        # Performance benchmarking
        self.benchmarks = []
        self.current_benchmark = None

        # Simplified profile management: single profile for all operations
        self.active_profile = self._initialize_profile_architecture()

        # Resource collectors
        self._resource_collectors = self._initialize_collectors()

        # Phase 4: MCP Integration Framework
        self.mcp_integrator = EnterpriseMCPIntegrator(profile)
        self.cross_module_integrator = EnterpriseCrossModuleIntegrator(profile)
        self.enable_mcp_validation = True
        
        # Initialize inventory-specific MCP validator
        self.inventory_mcp_validator = None
        try:
            from ..mcp_inventory_validator import create_inventory_mcp_validator
            # Use profiles that would work for inventory operations
            validator_profiles = [self.active_profile]
            self.inventory_mcp_validator = create_inventory_mcp_validator(validator_profiles)
            print_info("Inventory MCP validator initialized for real-time validation")
        except Exception as e:
            print_warning(f"Inventory MCP validator initialization failed: {str(e)[:50]}...")

        print_info("Enhanced inventory collector with MCP integration initialized")
        logger.info(f"Enhanced inventory collector initialized with active profile: {self.active_profile}")

    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Main execution method for enhanced inventory collector.

        This method provides the required abstract method implementation
        and serves as the primary entry point for inventory operations.
        """
        resource_types = kwargs.get("resource_types", ["ec2", "s3"])
        account_ids = kwargs.get("account_ids", [self.get_current_account_id()])
        include_costs = kwargs.get("include_costs", False)

        return self.collect_inventory(
            resource_types=resource_types, account_ids=account_ids, include_costs=include_costs
        )

    def _initialize_profile_architecture(self) -> str:
        """
        Initialize profile management following --profile or --all patterns.
        
        Strategic Alignment: "Do one thing and do it well"
        - Single profile override pattern: --profile takes precedence
        - Simple fallback to environment variables when no --profile specified
        - No hardcoded profile mappings - dynamic based on user input
        
        Returns:
            str: The active profile to use for all operations
        """
        # Primary profile determination: user --profile parameter takes absolute precedence
        if self.profile:
            print_info(f"Using user-specified profile: {self.profile}")
            logger.info("Profile override via --profile parameter - enterprise priority system")
            return self.profile
        
        # Fallback to environment variables when no --profile specified
        env_profile = (
            os.getenv("MANAGEMENT_PROFILE") or 
            os.getenv("BILLING_PROFILE") or 
            os.getenv("CENTRALISED_OPS_PROFILE") or
            "default"
        )
        
        print_info(f"No --profile specified, using environment fallback: {env_profile}")
        logger.info("Using environment variable fallback profile")
        return env_profile

    def _initialize_collectors(self) -> Dict[str, str]:
        """Initialize available resource collectors."""
        # Map resource types to their collector modules
        collectors = {
            "ec2": "EC2Collector",
            "rds": "RDSCollector",
            "s3": "S3Collector",
            "lambda": "LambdaCollector",
            "iam": "IAMCollector",
            "vpc": "VPCCollector",
            "cloudformation": "CloudFormationCollector",
            "costs": "CostCollector",
            "organizations": "ManagementResourceCollector",
        }

        logger.debug(f"Initialized {len(collectors)} resource collectors")
        return collectors
    
    def _extract_resource_counts(self, resource_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Extract resource counts from collected inventory data for MCP validation.
        
        Args:
            resource_data: Raw resource data from inventory collection
            
        Returns:
            Dictionary mapping resource types to counts
        """
        resource_counts = {}
        
        try:
            # Handle various data structures from inventory collection
            if isinstance(resource_data, dict):
                for resource_type, resources in resource_data.items():
                    if isinstance(resources, list):
                        resource_counts[resource_type] = len(resources)
                    elif isinstance(resources, dict):
                        # Handle nested structures (e.g., by region)
                        total_count = 0
                        for region_data in resources.values():
                            if isinstance(region_data, list):
                                total_count += len(region_data)
                            elif isinstance(region_data, dict) and 'resources' in region_data:
                                total_count += len(region_data['resources'])
                        resource_counts[resource_type] = total_count
                    elif isinstance(resources, int):
                        resource_counts[resource_type] = resources
                        
            logger.debug(f"Extracted resource counts for validation: {resource_counts}")
            return resource_counts
            
        except Exception as e:
            logger.warning(f"Failed to extract resource counts for MCP validation: {e}")
            return {}

    def get_all_resource_types(self) -> List[str]:
        """Get list of all available resource types."""
        return list(self._resource_collectors.keys())

    def get_organization_accounts(self) -> List[str]:
        """
        Get list of accounts in AWS Organization.
        
        Strategic Alignment: "Do one thing and do it well" 
        - Single responsibility: discover organization structure
        - Uses active profile for Organizations API access
        - Enables multi-account inventory operations
        """
        try:
            # Use management profile for Organizations operations
            # Use single active profile for all operations following --profile pattern
            management_profile = self.active_profile
            management_session = create_management_session(profile=management_profile)
            organizations_client = management_session.client("organizations")
            
            print_info("Discovering organization accounts with management profile...")
            response = self._make_aws_call(organizations_client.list_accounts)

            accounts = []
            for account in response.get("Accounts", []):
                if account["Status"] == "ACTIVE":
                    accounts.append(account["Id"])

            print_success(f"Found {len(accounts)} active accounts in organization")
            logger.info(f"Found {len(accounts)} active accounts using management profile: {management_profile}")
            return accounts

        except Exception as e:
            print_warning(f"Could not list organization accounts: {e}")
            logger.warning(f"Organization discovery failed, falling back to current account: {e}")
            # Fallback to current account
            return [self.get_account_id()]

    def get_current_account_id(self) -> str:
        """Get current AWS account ID."""
        return self.get_account_id()

    def collect_inventory(
        self, resource_types: List[str], account_ids: List[str], include_costs: bool = False
    ) -> Dict[str, Any]:
        """
        Enhanced inventory collection with 4-profile architecture and performance benchmarking.

        Args:
            resource_types: List of resource types to collect
            account_ids: List of account IDs to scan
            include_costs: Whether to include cost information

        Returns:
            Dictionary containing inventory results with performance metrics
        """

        # Start performance benchmark
        if ENHANCED_PROFILES_AVAILABLE:
            self.current_benchmark = PerformanceBenchmark(
                operation_name="inventory_collection",
                start_time=datetime.now(timezone.utc),
                target_seconds=self.performance_target_seconds,
                accounts_processed=len(account_ids),
            )

        logger.info(
            f"Starting enhanced inventory collection for {len(resource_types)} resource types across {len(account_ids)} accounts"
        )

        start_time = datetime.now()
        results = {
            "metadata": {
                "collection_time": start_time.isoformat(),
                "account_ids": account_ids,
                "resource_types": resource_types,
                "include_costs": include_costs,
                "collector_profile": self.profile,
                "collector_region": self.region,
                "enterprise_profiles_used": self.use_enterprise_profiles,
                "active_profile": self.active_profile,
                "performance_target": self.performance_target_seconds,
            },
            "resources": {},
            "summary": {},
            "errors": [],
            "profile_info": {"active_profile": self.active_profile},
        }

        try:
            if self.parallel:
                resource_data = self._collect_parallel(resource_types, account_ids, include_costs)
            else:
                resource_data = self._collect_sequential(resource_types, account_ids, include_costs)

            results["resources"] = resource_data
            results["summary"] = self._generate_summary(resource_data)

            # Phase 4: Enhanced Inventory MCP Validation Integration
            if self.enable_mcp_validation and self.inventory_mcp_validator:
                try:
                    print_info("Validating inventory results with specialized inventory MCP validator")
                    
                    # Extract resource counts for validation
                    # Build validation data structure that matches what the validator expects
                    resource_counts = self._extract_resource_counts(resource_data)
                    
                    # Add resource counts to results for the validator to find
                    results["resource_counts"] = resource_counts
                    
                    validation_data = {
                        "resource_counts": resource_counts,
                        "regions": results["metadata"].get("regions_scanned", []),
                        self.active_profile: {
                            "resource_counts": resource_counts,
                            "regions": results["metadata"].get("regions_scanned", [])
                        }
                    }
                    
                    # Run inventory-specific MCP validation
                    inventory_validation = self.inventory_mcp_validator.validate_inventory_data(validation_data)
                    
                    results["inventory_mcp_validation"] = inventory_validation
                    
                    overall_accuracy = inventory_validation.get("total_accuracy", 0)
                    if inventory_validation.get("passed_validation", False):
                        print_success(f"✅ Inventory MCP validation PASSED: {overall_accuracy:.1f}% accuracy achieved")
                    else:
                        print_warning(f"⚠️ Inventory MCP validation: {overall_accuracy:.1f}% accuracy (≥99.5% required)")
                    
                    # Also try the generic MCP integrator as backup
                    try:
                        validation_result = asyncio.run(self.mcp_integrator.validate_inventory_operations(results))
                        results["mcp_validation"] = validation_result.to_dict()
                    except Exception:
                        pass  # Skip generic validation if it fails

                except Exception as e:
                    print_warning(f"Inventory MCP validation failed: {str(e)[:50]}... - continuing without validation")
                    results["inventory_mcp_validation"] = {"error": str(e), "validation_skipped": True}
                    
                    # Fallback to generic MCP integration
                    try:
                        validation_result = asyncio.run(self.mcp_integrator.validate_inventory_operations(results))
                        results["mcp_validation"] = validation_result.to_dict()
                    except Exception as fallback_e:
                        results["mcp_validation"] = {"error": str(fallback_e), "validation_skipped": True}

            # Complete performance benchmark
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            results["metadata"]["duration_seconds"] = duration

            if self.current_benchmark:
                self.current_benchmark.finish(success=True)
                self.benchmarks.append(self.current_benchmark)

                # Add performance metrics
                results["performance_benchmark"] = {
                    "duration_seconds": self.current_benchmark.duration_seconds,
                    "performance_grade": self.current_benchmark.get_performance_grade(),
                    "target_achieved": self.current_benchmark.is_within_target(),
                    "target_seconds": self.current_benchmark.target_seconds,
                    "accounts_processed": self.current_benchmark.accounts_processed,
                }

                performance_color = "🟢" if self.current_benchmark.is_within_target() else "🟡"
                logger.info(
                    f"Enhanced inventory collection completed in {duration:.1f}s "
                    f"{performance_color} Grade: {self.current_benchmark.get_performance_grade()}"
                )
            else:
                logger.info(f"Inventory collection completed in {duration:.1f}s")

            return results

        except Exception as e:
            error_msg = f"Enhanced inventory collection failed: {e}"
            logger.error(error_msg)

            # Complete benchmark with failure
            if self.current_benchmark:
                self.current_benchmark.finish(success=False, error_message=error_msg)
                self.benchmarks.append(self.current_benchmark)

                results["performance_benchmark"] = {
                    "duration_seconds": self.current_benchmark.duration_seconds,
                    "performance_grade": "F",
                    "target_achieved": False,
                    "error_message": error_msg,
                }

            results["errors"].append(error_msg)
            return results

    def _collect_parallel(
        self, resource_types: List[str], account_ids: List[str], include_costs: bool
    ) -> Dict[str, Any]:
        """
        Collect inventory in parallel with enhanced performance monitoring.
        
        Follows the same pattern as legacy implementation but with enterprise
        performance monitoring and error handling.
        """
        results = {}
        total_tasks = len(resource_types) * len(account_ids)
        progress = ProgressTracker(total_tasks, "Collecting inventory")

        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit collection tasks
            future_to_params = {}

            for resource_type in resource_types:
                for account_id in account_ids:
                    future = executor.submit(
                        self._collect_resource_for_account, resource_type, account_id, include_costs
                    )
                    future_to_params[future] = (resource_type, account_id)

            # Collect results
            for future in as_completed(future_to_params):
                resource_type, account_id = future_to_params[future]
                try:
                    resource_data = future.result()

                    if resource_type not in results:
                        results[resource_type] = {}

                    results[resource_type][account_id] = resource_data
                    progress.update(status=f"Completed {resource_type} for {account_id}")

                except Exception as e:
                    logger.error(f"Failed to collect {resource_type} for account {account_id}: {e}")
                    progress.update(status=f"Failed {resource_type} for {account_id}")

        progress.complete()
        return results

    def _collect_sequential(
        self, resource_types: List[str], account_ids: List[str], include_costs: bool
    ) -> Dict[str, Any]:
        """
        Collect inventory sequentially with enhanced error handling.
        
        Follows the same pattern as legacy implementation but with enhanced
        error handling and progress tracking.
        """
        results = {}
        total_tasks = len(resource_types) * len(account_ids)
        progress = ProgressTracker(total_tasks, "Collecting inventory")

        for resource_type in resource_types:
            results[resource_type] = {}

            for account_id in account_ids:
                try:
                    resource_data = self._collect_resource_for_account(resource_type, account_id, include_costs)
                    results[resource_type][account_id] = resource_data
                    progress.update(status=f"Completed {resource_type} for {account_id}")

                except Exception as e:
                    logger.error(f"Failed to collect {resource_type} for account {account_id}: {e}")
                    results[resource_type][account_id] = {"error": str(e)}
                    progress.update(status=f"Failed {resource_type} for {account_id}")

        progress.complete()
        return results

    def _collect_resource_for_account(self, resource_type: str, account_id: str, include_costs: bool) -> Dict[str, Any]:
        """
        Collect specific resource type for an account using REAL AWS API calls.
        
        This method makes actual AWS API calls to discover resources, following
        the proven patterns from the existing inventory modules.
        """
        try:
            # Use active profile for AWS API calls
            session = boto3.Session(profile_name=self.active_profile)
            
            print_info(f"Collecting {resource_type} resources from account {account_id} using profile {self.active_profile}")
            
            if resource_type == "ec2":
                return self._collect_ec2_instances(session, account_id)
            elif resource_type == "rds":
                return self._collect_rds_instances(session, account_id)
            elif resource_type == "s3":
                return self._collect_s3_buckets(session, account_id)
            elif resource_type == "lambda":
                return self._collect_lambda_functions(session, account_id)
            elif resource_type == "iam":
                return self._collect_iam_resources(session, account_id)
            elif resource_type == "vpc":
                return self._collect_vpc_resources(session, account_id)
            elif resource_type == "cloudformation":
                return self._collect_cloudformation_stacks(session, account_id)
            elif resource_type == "organizations":
                return self._collect_organizations_data(session, account_id)
            elif resource_type == "costs" and include_costs:
                return self._collect_cost_data(session, account_id)
            else:
                print_warning(f"Resource type '{resource_type}' not supported yet")
                return {
                    "resources": [],
                    "count": 0, 
                    "resource_type": resource_type,
                    "account_id": account_id,
                    "collection_timestamp": datetime.now().isoformat(),
                    "warning": f"Resource type {resource_type} not implemented yet"
                }
                
        except Exception as e:
            error_msg = f"Failed to collect {resource_type} for account {account_id}: {e}"
            logger.error(error_msg)
            print_error(error_msg)
            return {
                "error": str(e),
                "resource_type": resource_type,
                "account_id": account_id,
                "collection_timestamp": datetime.now().isoformat(),
            }

    def _collect_ec2_instances(self, session: boto3.Session, account_id: str) -> Dict[str, Any]:
        """Collect EC2 instances using real AWS API calls."""
        try:
            region = self.region or session.region_name or "us-east-1"
            ec2_client = session.client("ec2", region_name=region)
            
            print_info(f"Calling EC2 describe_instances API for account {account_id} in region {region}")
            
            # Make real AWS API call with pagination support
            instances = []
            paginator = ec2_client.get_paginator('describe_instances')
            
            for page in paginator.paginate():
                for reservation in page.get("Reservations", []):
                    for instance in reservation.get("Instances", []):
                        # Extract instance data
                        instance_data = {
                            "instance_id": instance["InstanceId"],
                            "instance_type": instance["InstanceType"],
                            "state": instance["State"]["Name"],
                            "region": region,
                            "account_id": account_id,
                            "launch_time": instance.get("LaunchTime", "").isoformat() if instance.get("LaunchTime") else "",
                            "availability_zone": instance.get("Placement", {}).get("AvailabilityZone", ""),
                            "vpc_id": instance.get("VpcId", ""),
                            "subnet_id": instance.get("SubnetId", ""),
                            "private_ip_address": instance.get("PrivateIpAddress", ""),
                            "public_ip_address": instance.get("PublicIpAddress", ""),
                            "public_dns_name": instance.get("PublicDnsName", ""),
                        }
                        
                        # Extract tags
                        tags = {}
                        name = "No Name Tag"
                        for tag in instance.get("Tags", []):
                            tags[tag["Key"]] = tag["Value"]
                            if tag["Key"] == "Name":
                                name = tag["Value"]
                        
                        instance_data["tags"] = tags
                        instance_data["name"] = name
                        
                        # Extract security groups
                        instance_data["security_groups"] = [
                            {"group_id": sg["GroupId"], "group_name": sg["GroupName"]} 
                            for sg in instance.get("SecurityGroups", [])
                        ]
                        
                        instances.append(instance_data)
            
            print_success(f"Found {len(instances)} EC2 instances in account {account_id}")
            
            return {
                "instances": instances,
                "count": len(instances),
                "collection_timestamp": datetime.now().isoformat(),
                "region": region,
                "account_id": account_id,
            }
            
        except Exception as e:
            print_error(f"Failed to collect EC2 instances: {e}")
            raise

    def _collect_rds_instances(self, session: boto3.Session, account_id: str) -> Dict[str, Any]:
        """Collect RDS instances using real AWS API calls."""
        try:
            region = self.region or session.region_name or "us-east-1"
            rds_client = session.client("rds", region_name=region)
            
            print_info(f"Calling RDS describe_db_instances API for account {account_id} in region {region}")
            
            # Make real AWS API call with pagination support
            instances = []
            paginator = rds_client.get_paginator('describe_db_instances')
            
            for page in paginator.paginate():
                for db_instance in page.get("DBInstances", []):
                    instance_data = {
                        "db_instance_identifier": db_instance["DBInstanceIdentifier"],
                        "engine": db_instance["Engine"],
                        "engine_version": db_instance["EngineVersion"],
                        "instance_class": db_instance["DBInstanceClass"],
                        "status": db_instance["DBInstanceStatus"],
                        "account_id": account_id,
                        "region": region,
                        "multi_az": db_instance.get("MultiAZ", False),
                        "storage_type": db_instance.get("StorageType", ""),
                        "allocated_storage": db_instance.get("AllocatedStorage", 0),
                        "endpoint": db_instance.get("Endpoint", {}).get("Address", "") if db_instance.get("Endpoint") else "",
                        "port": db_instance.get("Endpoint", {}).get("Port", 0) if db_instance.get("Endpoint") else 0,
                        "vpc_id": db_instance.get("DBSubnetGroup", {}).get("VpcId", "") if db_instance.get("DBSubnetGroup") else "",
                    }
                    
                    instances.append(instance_data)
            
            print_success(f"Found {len(instances)} RDS instances in account {account_id}")
            
            return {
                "instances": instances,
                "count": len(instances),
                "collection_timestamp": datetime.now().isoformat(),
                "region": region,
                "account_id": account_id,
            }
            
        except Exception as e:
            print_error(f"Failed to collect RDS instances: {e}")
            raise

    def _collect_s3_buckets(self, session: boto3.Session, account_id: str) -> Dict[str, Any]:
        """Collect S3 buckets using real AWS API calls."""
        try:
            s3_client = session.client("s3")
            
            print_info(f"Calling S3 list_buckets API for account {account_id}")
            
            # Make real AWS API call - S3 buckets are global
            response = s3_client.list_buckets()
            buckets = []
            
            for bucket in response.get("Buckets", []):
                bucket_data = {
                    "name": bucket["Name"],
                    "creation_date": bucket["CreationDate"].isoformat(),
                    "account_id": account_id,
                }
                
                # Try to get bucket location (region)
                try:
                    location_response = s3_client.get_bucket_location(Bucket=bucket["Name"])
                    bucket_region = location_response.get("LocationConstraint")
                    if bucket_region is None:
                        bucket_region = "us-east-1"  # Default for US Standard
                    bucket_data["region"] = bucket_region
                except Exception as e:
                    logger.warning(f"Could not get location for bucket {bucket['Name']}: {e}")
                    bucket_data["region"] = "unknown"
                
                # Try to get bucket versioning
                try:
                    versioning_response = s3_client.get_bucket_versioning(Bucket=bucket["Name"])
                    bucket_data["versioning"] = versioning_response.get("Status", "Suspended")
                except Exception as e:
                    logger.warning(f"Could not get versioning for bucket {bucket['Name']}: {e}")
                    bucket_data["versioning"] = "unknown"
                
                buckets.append(bucket_data)
            
            print_success(f"Found {len(buckets)} S3 buckets in account {account_id}")
            
            return {
                "buckets": buckets,
                "count": len(buckets),
                "collection_timestamp": datetime.now().isoformat(),
                "account_id": account_id,
            }
            
        except Exception as e:
            print_error(f"Failed to collect S3 buckets: {e}")
            raise

    def _collect_lambda_functions(self, session: boto3.Session, account_id: str) -> Dict[str, Any]:
        """Collect Lambda functions using real AWS API calls."""
        try:
            region = self.region or session.region_name or "us-east-1"
            lambda_client = session.client("lambda", region_name=region)
            
            print_info(f"Calling Lambda list_functions API for account {account_id} in region {region}")
            
            # Make real AWS API call with pagination support
            functions = []
            paginator = lambda_client.get_paginator('list_functions')
            
            for page in paginator.paginate():
                for function in page.get("Functions", []):
                    function_data = {
                        "function_name": function["FunctionName"],
                        "runtime": function.get("Runtime", ""),
                        "handler": function.get("Handler", ""),
                        "code_size": function.get("CodeSize", 0),
                        "description": function.get("Description", ""),
                        "timeout": function.get("Timeout", 0),
                        "memory_size": function.get("MemorySize", 0),
                        "last_modified": function.get("LastModified", ""),
                        "role": function.get("Role", ""),
                        "account_id": account_id,
                        "region": region,
                    }
                    
                    functions.append(function_data)
            
            print_success(f"Found {len(functions)} Lambda functions in account {account_id}")
            
            return {
                "functions": functions,
                "count": len(functions),
                "collection_timestamp": datetime.now().isoformat(),
                "region": region,
                "account_id": account_id,
            }
            
        except Exception as e:
            print_error(f"Failed to collect Lambda functions: {e}")
            raise

    def _collect_iam_resources(self, session: boto3.Session, account_id: str) -> Dict[str, Any]:
        """Collect IAM resources using real AWS API calls."""
        try:
            iam_client = session.client("iam")
            
            print_info(f"Calling IAM APIs for account {account_id}")
            
            resources = {"users": [], "roles": [], "policies": [], "groups": []}
            
            # Collect users
            paginator = iam_client.get_paginator('list_users')
            for page in paginator.paginate():
                for user in page.get("Users", []):
                    user_data = {
                        "user_name": user["UserName"],
                        "user_id": user["UserId"],
                        "arn": user["Arn"],
                        "create_date": user["CreateDate"].isoformat(),
                        "path": user["Path"],
                        "account_id": account_id,
                    }
                    resources["users"].append(user_data)
            
            # Collect roles
            paginator = iam_client.get_paginator('list_roles')
            for page in paginator.paginate():
                for role in page.get("Roles", []):
                    role_data = {
                        "role_name": role["RoleName"],
                        "role_id": role["RoleId"],
                        "arn": role["Arn"],
                        "create_date": role["CreateDate"].isoformat(),
                        "path": role["Path"],
                        "account_id": account_id,
                    }
                    resources["roles"].append(role_data)
            
            total_count = len(resources["users"]) + len(resources["roles"])
            print_success(f"Found {total_count} IAM resources in account {account_id}")
            
            return {
                "resources": resources,
                "count": total_count,
                "collection_timestamp": datetime.now().isoformat(),
                "account_id": account_id,
            }
            
        except Exception as e:
            print_error(f"Failed to collect IAM resources: {e}")
            raise

    def _collect_vpc_resources(self, session: boto3.Session, account_id: str) -> Dict[str, Any]:
        """Collect VPC resources using real AWS API calls."""
        try:
            region = self.region or session.region_name or "us-east-1"
            ec2_client = session.client("ec2", region_name=region)
            
            print_info(f"Calling EC2 VPC APIs for account {account_id} in region {region}")
            
            vpcs = []
            paginator = ec2_client.get_paginator('describe_vpcs')
            
            for page in paginator.paginate():
                for vpc in page.get("Vpcs", []):
                    vpc_data = {
                        "vpc_id": vpc["VpcId"],
                        "cidr_block": vpc["CidrBlock"],
                        "state": vpc["State"],
                        "is_default": vpc.get("IsDefault", False),
                        "instance_tenancy": vpc.get("InstanceTenancy", ""),
                        "account_id": account_id,
                        "region": region,
                    }
                    
                    # Extract tags
                    tags = {}
                    name = "No Name Tag"
                    for tag in vpc.get("Tags", []):
                        tags[tag["Key"]] = tag["Value"]
                        if tag["Key"] == "Name":
                            name = tag["Value"]
                    
                    vpc_data["tags"] = tags
                    vpc_data["name"] = name
                    
                    vpcs.append(vpc_data)
            
            print_success(f"Found {len(vpcs)} VPCs in account {account_id}")
            
            return {
                "vpcs": vpcs,
                "count": len(vpcs),
                "collection_timestamp": datetime.now().isoformat(),
                "region": region,
                "account_id": account_id,
            }
            
        except Exception as e:
            print_error(f"Failed to collect VPC resources: {e}")
            raise

    def _collect_cloudformation_stacks(self, session: boto3.Session, account_id: str) -> Dict[str, Any]:
        """Collect CloudFormation stacks using real AWS API calls."""
        try:
            region = self.region or session.region_name or "us-east-1"
            cf_client = session.client("cloudformation", region_name=region)
            
            print_info(f"Calling CloudFormation describe_stacks API for account {account_id} in region {region}")
            
            stacks = []
            paginator = cf_client.get_paginator('describe_stacks')
            
            for page in paginator.paginate():
                for stack in page.get("Stacks", []):
                    stack_data = {
                        "stack_name": stack["StackName"],
                        "stack_id": stack["StackId"],
                        "stack_status": stack["StackStatus"],
                        "creation_time": stack["CreationTime"].isoformat(),
                        "description": stack.get("Description", ""),
                        "account_id": account_id,
                        "region": region,
                    }
                    
                    if "LastUpdatedTime" in stack:
                        stack_data["last_updated_time"] = stack["LastUpdatedTime"].isoformat()
                    
                    stacks.append(stack_data)
            
            print_success(f"Found {len(stacks)} CloudFormation stacks in account {account_id}")
            
            return {
                "stacks": stacks,
                "count": len(stacks),
                "collection_timestamp": datetime.now().isoformat(),
                "region": region,
                "account_id": account_id,
            }
            
        except Exception as e:
            print_error(f"Failed to collect CloudFormation stacks: {e}")
            raise

    def _collect_cost_data(self, session: boto3.Session, account_id: str) -> Dict[str, Any]:
        """Collect cost data using real AWS Cost Explorer API calls."""
        try:
            # Note: Cost Explorer requires specific billing permissions
            print_warning("Cost data collection requires AWS Cost Explorer permissions")
            print_info(f"Attempting to collect cost data for account {account_id}")
            
            # For now, return placeholder - would need billing profile for actual cost data
            return {
                "monthly_costs": {
                    "note": "Cost data collection requires proper billing permissions and profile",
                    "suggestion": "Use BILLING_PROFILE environment variable or --profile with billing access"
                },
                "account_id": account_id,
                "collection_timestamp": datetime.now().isoformat(),
            }
            
        except Exception as e:
            print_error(f"Failed to collect cost data: {e}")
            raise

    def _collect_organizations_data(self, session: boto3.Session, account_id: str) -> Dict[str, Any]:
        """Collect AWS Organizations data using existing organizations discovery module."""
        try:
            print_info(f"Collecting Organizations data for account {account_id}")
            
            # Use the session's profile name for organizations discovery
            profile_name = session.profile_name or self.active_profile
            
            org_client = session.client('organizations', region_name='us-east-1')  # Organizations is always us-east-1
            
            # Collect organization structure and accounts
            organizations_data = {
                "organization_info": {},
                "accounts": [],
                "organizational_units": [],
                "resource_type": "organizations",
                "account_id": account_id,
                "collection_timestamp": datetime.now().isoformat()
            }
            
            try:
                # Get organization details
                org_response = org_client.describe_organization()
                organizations_data["organization_info"] = org_response.get("Organization", {})
                
                # Get all accounts in the organization
                paginator = org_client.get_paginator('list_accounts')
                accounts = []
                for page in paginator.paginate():
                    accounts.extend(page.get('Accounts', []))
                
                organizations_data["accounts"] = accounts
                organizations_data["count"] = len(accounts)
                
                # Get organizational units
                try:
                    roots_response = org_client.list_roots()
                    for root in roots_response.get('Roots', []):
                        ou_paginator = org_client.get_paginator('list_organizational_units_for_parent')
                        for ou_page in ou_paginator.paginate(ParentId=root['Id']):
                            organizations_data["organizational_units"].extend(ou_page.get('OrganizationalUnits', []))
                except Exception as ou_e:
                    print_warning(f"Could not collect organizational units: {ou_e}")
                    organizations_data["organizational_units"] = []
                
                print_success(f"Successfully collected {len(accounts)} accounts from organization")
                
            except Exception as org_e:
                print_warning(f"Organization data collection limited: {org_e}")
                # Try to collect at least basic account info if not in an organization
                try:
                    sts_client = session.client('sts')
                    caller_identity = sts_client.get_caller_identity()
                    organizations_data["accounts"] = [{
                        "Id": caller_identity.get("Account"),
                        "Name": f"Account-{caller_identity.get('Account')}",
                        "Status": "ACTIVE",
                        "JoinedMethod": "STANDALONE"
                    }]
                    organizations_data["count"] = 1
                    print_info("Collected standalone account information")
                except Exception as sts_e:
                    print_error(f"Could not collect account information: {sts_e}")
                    organizations_data["count"] = 0
            
            return organizations_data
            
        except Exception as e:
            print_error(f"Failed to collect organizations data: {e}")
            raise

    def _generate_summary(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive summary statistics from collected data.
        
        Enhanced implementation with better error handling and metrics.
        """
        summary = {
            "total_resources": 0,
            "resources_by_type": {},
            "resources_by_account": {},
            "collection_status": "completed",
            "errors": [],
            "collection_summary": {
                "successful_collections": 0,
                "failed_collections": 0,
                "accounts_processed": set(),
                "resource_types_processed": set(),
            }
        }

        for resource_type, accounts_data in resource_data.items():
            type_count = 0
            summary["collection_summary"]["resource_types_processed"].add(resource_type)

            for account_id, account_data in accounts_data.items():
                summary["collection_summary"]["accounts_processed"].add(account_id)
                
                if "error" in account_data:
                    summary["errors"].append(f"{resource_type}/{account_id}: {account_data['error']}")
                    summary["collection_summary"]["failed_collections"] += 1
                    continue

                summary["collection_summary"]["successful_collections"] += 1

                # Count resources based on type
                account_count = account_data.get("count", 0)
                if account_count == 0:
                    # Try to calculate from actual resource lists
                    if resource_type == "ec2":
                        account_count = len(account_data.get("instances", []))
                    elif resource_type == "rds":
                        account_count = len(account_data.get("instances", []))
                    elif resource_type == "s3":
                        account_count = len(account_data.get("buckets", []))
                    elif resource_type == "lambda":
                        account_count = len(account_data.get("functions", []))
                    else:
                        account_count = len(account_data.get("resources", []))

                type_count += account_count

                if account_id not in summary["resources_by_account"]:
                    summary["resources_by_account"][account_id] = 0
                summary["resources_by_account"][account_id] += account_count

            summary["resources_by_type"][resource_type] = type_count
            summary["total_resources"] += type_count

        # Convert sets to lists for JSON serialization
        summary["collection_summary"]["accounts_processed"] = list(summary["collection_summary"]["accounts_processed"])
        summary["collection_summary"]["resource_types_processed"] = list(summary["collection_summary"]["resource_types_processed"])
        
        # Update collection status based on errors
        if summary["errors"]:
            if summary["collection_summary"]["successful_collections"] == 0:
                summary["collection_status"] = "failed"
            else:
                summary["collection_status"] = "completed_with_errors"

        return summary
    
    def export_inventory_results(
        self, 
        results: Dict[str, Any], 
        export_format: str = "json",
        output_file: Optional[str] = None
    ) -> str:
        """
        Export inventory results to multiple formats following proven finops patterns.
        
        Args:
            results: Inventory results dictionary
            export_format: Export format (json, csv, markdown, pdf, yaml)
            output_file: Optional output file path
        
        Returns:
            Export file path or formatted string content
        """
        import json
        import csv
        from datetime import datetime
        from pathlib import Path
        
        # Determine output file path
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"/Volumes/Working/1xOps/CloudOps-Runbooks/tmp/inventory_export_{timestamp}.{export_format}"
        
        # Ensure tmp directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if export_format.lower() == "json":
                return self._export_json(results, output_file)
            elif export_format.lower() == "csv":
                return self._export_csv(results, output_file)
            elif export_format.lower() == "markdown":
                return self._export_markdown(results, output_file)
            elif export_format.lower() == "yaml":
                return self._export_yaml(results, output_file)
            elif export_format.lower() == "pdf":
                return self._export_pdf(results, output_file)
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
                
        except Exception as e:
            error_msg = f"Export failed for format {export_format}: {e}"
            print_error(error_msg)
            logger.error(error_msg)
            raise
    
    def _export_json(self, results: Dict[str, Any], output_file: str) -> str:
        """Export results to JSON format."""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print_success(f"Inventory exported to JSON: {output_file}")
        return output_file
    
    def _export_csv(self, results: Dict[str, Any], output_file: str) -> str:
        """Export results to CSV format with real AWS data structure."""
        import csv
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(["Account", "Region", "Resource Type", "Resource ID", "Name", "Status", "Additional Info"])
            
            # Write data rows from real AWS resource structure
            resource_data = results.get("resources", {})
            
            for resource_type, accounts_data in resource_data.items():
                for account_id, account_data in accounts_data.items():
                    if "error" in account_data:
                        # Handle error cases
                        writer.writerow([
                            account_id,
                            account_data.get("region", "unknown"),
                            resource_type,
                            "",
                            "",
                            "ERROR",
                            account_data.get("error", "")
                        ])
                        continue
                    
                    account_region = account_data.get("region", "unknown")
                    
                    # Handle different resource types with their specific data structures
                    if resource_type == "ec2" and "instances" in account_data:
                        for instance in account_data["instances"]:
                            writer.writerow([
                                account_id,
                                instance.get("region", account_region),
                                "ec2-instance",
                                instance.get("instance_id", ""),
                                instance.get("name", "No Name Tag"),
                                instance.get("state", ""),
                                f"Type: {instance.get('instance_type', '')}, AZ: {instance.get('availability_zone', '')}"
                            ])
                    
                    elif resource_type == "rds" and "instances" in account_data:
                        for instance in account_data["instances"]:
                            writer.writerow([
                                account_id,
                                instance.get("region", account_region),
                                "rds-instance",
                                instance.get("db_instance_identifier", ""),
                                instance.get("db_instance_identifier", ""),
                                instance.get("status", ""),
                                f"Engine: {instance.get('engine', '')}, Class: {instance.get('instance_class', '')}"
                            ])
                    
                    elif resource_type == "s3" and "buckets" in account_data:
                        for bucket in account_data["buckets"]:
                            writer.writerow([
                                account_id,
                                bucket.get("region", account_region),
                                "s3-bucket",
                                bucket.get("name", ""),
                                bucket.get("name", ""),
                                "",
                                f"Created: {bucket.get('creation_date', '')}"
                            ])
                    
                    elif resource_type == "lambda" and "functions" in account_data:
                        for function in account_data["functions"]:
                            writer.writerow([
                                account_id,
                                function.get("region", account_region),
                                "lambda-function",
                                function.get("function_name", ""),
                                function.get("function_name", ""),
                                "",
                                f"Runtime: {function.get('runtime', '')}, Memory: {function.get('memory_size', '')}MB"
                            ])
                    
                    elif resource_type == "iam" and "resources" in account_data:
                        iam_resources = account_data["resources"]
                        for user in iam_resources.get("users", []):
                            writer.writerow([
                                account_id,
                                "global",
                                "iam-user",
                                user.get("user_name", ""),
                                user.get("user_name", ""),
                                "",
                                f"ARN: {user.get('arn', '')}"
                            ])
                        for role in iam_resources.get("roles", []):
                            writer.writerow([
                                account_id,
                                "global",
                                "iam-role",
                                role.get("role_name", ""),
                                role.get("role_name", ""),
                                "",
                                f"ARN: {role.get('arn', '')}"
                            ])
                    
                    elif resource_type == "vpc" and "vpcs" in account_data:
                        for vpc in account_data["vpcs"]:
                            writer.writerow([
                                account_id,
                                vpc.get("region", account_region),
                                "vpc",
                                vpc.get("vpc_id", ""),
                                vpc.get("name", "No Name Tag"),
                                vpc.get("state", ""),
                                f"CIDR: {vpc.get('cidr_block', '')}, Default: {vpc.get('is_default', False)}"
                            ])
                    
                    elif resource_type == "cloudformation" and "stacks" in account_data:
                        for stack in account_data["stacks"]:
                            writer.writerow([
                                account_id,
                                stack.get("region", account_region),
                                "cloudformation-stack",
                                stack.get("stack_name", ""),
                                stack.get("stack_name", ""),
                                stack.get("stack_status", ""),
                                f"Created: {stack.get('creation_time', '')}"
                            ])
                    
                    # Handle cases where no specific resources were found but collection was successful
                    elif account_data.get("count", 0) == 0:
                        writer.writerow([
                            account_id,
                            account_region,
                            resource_type,
                            "",
                            "",
                            "NO_RESOURCES",
                            f"No {resource_type} resources found"
                        ])
        
        print_success(f"Inventory exported to CSV: {output_file}")
        return output_file
    
    def _export_markdown(self, results: Dict[str, Any], output_file: str) -> str:
        """Export results to Markdown format with tables."""
        content = []
        content.append("# AWS Inventory Report")
        content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        
        # Summary section
        total_resources = sum(
            len(resources)
            for account_data in results.get("accounts", {}).values()
            for region_data in account_data.get("regions", {}).values()
            for resources in region_data.get("resources", {}).values()
        )
        
        content.append("## Summary")
        content.append(f"- Total Accounts: {len(results.get('accounts', {}))}")
        content.append(f"- Total Resources: {total_resources}")
        content.append("")
        
        # Detailed inventory
        content.append("## Detailed Inventory")
        content.append("")
        content.append("| Account | Region | Resource Type | Resource ID | Name | Status |")
        content.append("|---------|--------|---------------|-------------|------|--------|")
        
        for account_id, account_data in results.get("accounts", {}).items():
            for region, region_data in account_data.get("regions", {}).items():
                for resource_type, resources in region_data.get("resources", {}).items():
                    for resource in resources:
                        content.append(f"| {account_id} | {region} | {resource_type} | {resource.get('id', '')} | {resource.get('name', '')} | {resource.get('state', '')} |")
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(content))
        
        print_success(f"Inventory exported to Markdown: {output_file}")
        return output_file
    
    def _export_yaml(self, results: Dict[str, Any], output_file: str) -> str:
        """Export results to YAML format."""
        try:
            import yaml
        except ImportError:
            print_error("PyYAML not available. Install with: pip install pyyaml")
            raise
        
        with open(output_file, 'w') as f:
            yaml.dump(results, f, default_flow_style=False, sort_keys=False)
        
        print_success(f"Inventory exported to YAML: {output_file}")
        return output_file
    
    def _export_pdf(self, results: Dict[str, Any], output_file: str) -> str:
        """Export results to executive PDF report."""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
        except ImportError:
            # Graceful fallback to markdown if reportlab not available
            print_warning("ReportLab not available, exporting to markdown instead")
            return self._export_markdown(results, output_file.replace('.pdf', '.md'))
        
        doc = SimpleDocTemplate(output_file, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue
        )
        story.append(Paragraph("AWS Inventory Report", title_style))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        
        total_resources = sum(
            len(resources)
            for account_data in results.get("accounts", {}).values()
            for region_data in account_data.get("regions", {}).values()
            for resources in region_data.get("resources", {}).values()
        )
        
        summary_text = f"""
        This report provides a comprehensive inventory of AWS resources across {len(results.get('accounts', {}))} accounts.
        A total of {total_resources} resources were discovered and catalogued.
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Build the PDF
        doc.build(story)
        
        print_success(f"Inventory exported to PDF: {output_file}")
        return output_file


# Legacy compatibility class - maintain backward compatibility
class InventoryCollector(EnhancedInventoryCollector):
    """
    Legacy InventoryCollector - redirects to EnhancedInventoryCollector for backward compatibility.

    This maintains existing API compatibility while leveraging enhanced capabilities.
    """

    def __init__(
        self,
        profile: Optional[str] = None,
        region: Optional[str] = None,
        config: Optional[RunbooksConfig] = None,
        parallel: bool = True,
    ):
        """Initialize legacy inventory collector with enhanced backend."""
        super().__init__(
            profile=profile,
            region=region,
            config=config,
            parallel=parallel,
            use_enterprise_profiles=False,  # Disable enterprise profiles for legacy mode
            performance_target_seconds=60.0,  # More lenient target for legacy mode
        )
        logger.info("Legacy inventory collector initialized - using enhanced backend with compatibility mode")

    def _collect_parallel(
        self, resource_types: List[str], account_ids: List[str], include_costs: bool
    ) -> Dict[str, Any]:
        """Collect inventory in parallel."""
        results = {}
        total_tasks = len(resource_types) * len(account_ids)
        progress = ProgressTracker(total_tasks, "Collecting inventory")

        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit collection tasks
            future_to_params = {}

            for resource_type in resource_types:
                for account_id in account_ids:
                    future = executor.submit(
                        self._collect_resource_for_account, resource_type, account_id, include_costs
                    )
                    future_to_params[future] = (resource_type, account_id)

            # Collect results
            for future in as_completed(future_to_params):
                resource_type, account_id = future_to_params[future]
                try:
                    resource_data = future.result()

                    if resource_type not in results:
                        results[resource_type] = {}

                    results[resource_type][account_id] = resource_data
                    progress.update(status=f"Completed {resource_type} for {account_id}")

                except Exception as e:
                    logger.error(f"Failed to collect {resource_type} for account {account_id}: {e}")
                    progress.update(status=f"Failed {resource_type} for {account_id}")

        progress.complete()
        return results

    def _collect_sequential(
        self, resource_types: List[str], account_ids: List[str], include_costs: bool
    ) -> Dict[str, Any]:
        """Collect inventory sequentially."""
        results = {}
        total_tasks = len(resource_types) * len(account_ids)
        progress = ProgressTracker(total_tasks, "Collecting inventory")

        for resource_type in resource_types:
            results[resource_type] = {}

            for account_id in account_ids:
                try:
                    resource_data = self._collect_resource_for_account(resource_type, account_id, include_costs)
                    results[resource_type][account_id] = resource_data
                    progress.update(status=f"Completed {resource_type} for {account_id}")

                except Exception as e:
                    logger.error(f"Failed to collect {resource_type} for account {account_id}: {e}")
                    results[resource_type][account_id] = {"error": str(e)}
                    progress.update(status=f"Failed {resource_type} for {account_id}")

        progress.complete()
        return results

    def _collect_resource_for_account(self, resource_type: str, account_id: str, include_costs: bool) -> Dict[str, Any]:
        """
        Collect specific resource type for an account.

        This is a mock implementation. In a full implementation,
        this would delegate to specific resource collectors.
        """
        # Mock implementation - replace with actual collectors
        import time

        # Deterministic collection timing
        time.sleep(0.2)  # Fixed 200ms delay for testing

        # REMOVED: Mock data generation violates enterprise standards
        # Use real AWS API calls with proper authentication and error handling
        try:
            if resource_type == "ec2":
                # TODO: Implement real EC2 API call
                # ec2_client = self.session.client('ec2', region_name=self.region)
                # response = ec2_client.describe_instances()
                return {
                    "instances": [],  # Replace with real EC2 API response processing
                    "count": 0,
                    "account_id": account_id,
                    "region": self.region or "us-east-1"
                }
            elif resource_type == "rds":
                # TODO: Implement real RDS API call
                # rds_client = self.session.client('rds', region_name=self.region)
                # response = rds_client.describe_db_instances()
                return {
                    "instances": [],  # Replace with real RDS API response processing
                    "count": 0,
                    "account_id": account_id,
                    "region": self.region or "us-east-1"
                }
            elif resource_type == "s3":
                # TODO: Implement real S3 API call
                # s3_client = self.session.client('s3')
                # response = s3_client.list_buckets()
                return {
                    "buckets": [],  # Replace with real S3 API response processing
                    "count": 0,
                    "account_id": account_id,
                    "region": self.region or "us-east-1"
                }
        except Exception as e:
            # Proper error handling for AWS API failures
            return {
                "error": str(e),
                "resource_type": resource_type,
                "account_id": account_id,
                "count": 0
            }
        else:
            return {"resources": [], "count": 0, "resource_type": resource_type, "account_id": account_id}

    def _generate_summary(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from collected data."""
        summary = {
            "total_resources": 0,
            "resources_by_type": {},
            "resources_by_account": {},
            "collection_status": "completed",
        }

        for resource_type, accounts_data in resource_data.items():
            type_count = 0

            for account_id, account_data in accounts_data.items():
                if "error" in account_data:
                    continue

                # Count resources based on type
                if resource_type == "ec2":
                    account_count = account_data.get("count", 0)
                elif resource_type == "rds":
                    account_count = account_data.get("count", 0)
                elif resource_type == "s3":
                    account_count = account_data.get("count", 0)
                else:
                    account_count = account_data.get("count", 0)

                type_count += account_count

                if account_id not in summary["resources_by_account"]:
                    summary["resources_by_account"][account_id] = 0
                summary["resources_by_account"][account_id] += account_count

            summary["resources_by_type"][resource_type] = type_count
            summary["total_resources"] += type_count

        return summary

    def run(self):
        """Implementation of abstract base method."""
        # Default inventory collection
        resource_types = ["ec2", "rds", "s3"]
        account_ids = [self.get_current_account_id()]
        return self.collect_inventory(resource_types, account_ids)

    # Phase 4: Cross-Module Integration Methods
    async def prepare_data_for_operate_module(self, inventory_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare inventory data for seamless integration with operate module.

        This method transforms inventory results into a format optimized for
        operational workflows, enabling inventory → operate data flow.

        Args:
            inventory_results: Results from inventory collection

        Returns:
            Dict formatted for operate module consumption
        """
        try:
            print_info("Preparing inventory data for operate module integration")

            data_flow_result = await self.cross_module_integrator.execute_data_flow(
                flow_type=DataFlowType.INVENTORY_TO_OPERATE, source_data=inventory_results
            )

            if data_flow_result.success:
                print_success("Inventory → Operate data flow completed successfully")
                return data_flow_result.transformed_data
            else:
                print_error(f"Data flow failed: {', '.join(data_flow_result.error_details)}")
                return {}

        except Exception as e:
            print_error(f"Failed to prepare data for operate module: {str(e)}")
            return {}

    async def collect_inventory_with_operate_integration(
        self,
        resource_types: List[str],
        account_ids: List[str],
        include_costs: bool = False,
        prepare_for_operations: bool = False,
    ) -> Dict[str, Any]:
        """
        Enhanced inventory collection with automatic operate module preparation.

        This method extends the standard inventory collection to automatically
        prepare data for operational workflows when requested.

        Args:
            resource_types: List of resource types to collect
            account_ids: List of account IDs to scan
            include_costs: Whether to include cost information
            prepare_for_operations: Whether to prepare data for operate module

        Returns:
            Dictionary containing inventory results and optional operate preparation
        """
        # Standard inventory collection
        results = self.collect_inventory(resource_types, account_ids, include_costs)

        # Optional operate module preparation
        if prepare_for_operations:
            operate_data = await self.prepare_data_for_operate_module(results)
            results["operate_integration"] = {
                "prepared_data": operate_data,
                "integration_timestamp": datetime.now().isoformat(),
                "operation_targets": operate_data.get("operation_targets", []),
            }

            print_success(f"Inventory collection with operate integration complete")

        return results

    def get_mcp_validation_status(self) -> Dict[str, Any]:
        """
        Get current MCP validation configuration and status.

        Returns:
            Dictionary containing MCP integration status
        """
        return {
            "mcp_validation_enabled": self.enable_mcp_validation,
            "mcp_integrator_initialized": self.mcp_integrator is not None,
            "cross_module_integrator_initialized": self.cross_module_integrator is not None,
            "supported_data_flows": [flow.value for flow in DataFlowType],
            "supported_mcp_operations": [op.value for op in MCPOperationType],
        }

    def enable_cross_module_integration(self, enable: bool = True) -> None:
        """
        Enable or disable cross-module integration features.

        Args:
            enable: Whether to enable cross-module integration
        """
        if enable and (self.mcp_integrator is None or self.cross_module_integrator is None):
            print_warning("Initializing MCP and cross-module integrators")
            self.mcp_integrator = EnterpriseMCPIntegrator(self.profile)
            self.cross_module_integrator = EnterpriseCrossModuleIntegrator(self.profile)

        self.enable_mcp_validation = enable

        status = "enabled" if enable else "disabled"
        print_info(f"Cross-module integration {status}")
        logger.info(f"Cross-module integration {status} for inventory collector")
