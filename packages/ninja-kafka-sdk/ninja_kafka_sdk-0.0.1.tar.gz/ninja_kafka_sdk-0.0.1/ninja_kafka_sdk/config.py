"""
Auto-configuration for Ninja Kafka SDK.
Detects environment and sets appropriate Kafka settings.
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class NinjaKafkaConfig:
    """Explicit configuration for Ninja Kafka SDK."""
    
    def __init__(
        self,
        kafka_servers: Optional[str] = None,
        consumer_group: Optional[str] = None,
        environment: Optional[str] = None,
        tasks_topic: str = 'ninja-tasks',
        results_topic: str = 'ninja-results'
    ):
        self.environment = environment or self._detect_environment()
        self.kafka_servers = kafka_servers or self._get_kafka_servers()
        self.tasks_topic = tasks_topic
        self.results_topic = results_topic
        self.consumer_group = consumer_group or self._get_consumer_group()
        self.producer_settings = self._get_producer_settings()
        self.consumer_settings = self._get_consumer_settings()
        
        logger.info(f"Ninja Kafka SDK configured for environment: {self.environment}")
        logger.info(f"Kafka servers: {self.kafka_servers}")
        logger.info(f"Consumer group: {self.consumer_group}")
    
    def _detect_environment(self) -> str:
        """Auto-detect environment from various sources."""
        # 1. Check environment variable
        env = os.getenv('KAFKA_CONNECTION', '').lower()
        if env in ['local', 'dev', 'stage', 'prod']:
            logger.debug(f"Environment detected from KAFKA_CONNECTION: {env}")
            return env
            
        # 2. Check local.py (following autologin pattern)
        env = self._check_local_py()
        if env:
            logger.debug(f"Environment detected from local.py: {env}")
            return env
            
        # 3. Check AWS metadata (if running on EC2)
        if self._is_aws_environment():
            logger.debug("AWS environment detected, defaulting to 'stage'")
            return 'stage'
            
        # 4. Default to local
        logger.debug("No environment detected, defaulting to 'local'")
        return 'local'
    
    def _check_local_py(self) -> Optional[str]:
        """Check local.py for configuration (following autologin pattern)."""
        try:
            import sys
            import importlib.util
            
            # Try different paths for local.py
            local_paths = [
                Path(__file__).parent.parent / 'app' / 'local.py',
                Path('/Users/lex-tech/Documents/dev/blazel/auto_login/app/local.py'),
                Path.cwd() / 'local.py',
                Path.cwd() / 'app' / 'local.py'
            ]
            
            for local_path in local_paths:
                if local_path.exists():
                    spec = importlib.util.spec_from_file_location('local', local_path)
                    local_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(local_module)
                    
                    if hasattr(local_module, 'KAFKA_CONNECTION'):
                        env = getattr(local_module, 'KAFKA_CONNECTION', 'local').lower()
                        logger.debug(f"Loaded KAFKA_CONNECTION='{env}' from {local_path}")
                        return env
        except Exception as e:
            logger.debug(f"Could not load local.py: {e}")
        
        return None
    
    def _get_consumer_group(self) -> str:
        """Auto-detect consumer group based on which service is using the SDK."""
        # Check if we're running in browser-ninja context
        import sys
        import os
        
        # Method 1: Check current working directory
        cwd = os.getcwd()
        if 'browser-ninja' in cwd:
            logger.debug("Detected browser-ninja context from working directory")
            return 'browser-ninja'
        
        # Method 2: Check if browser-ninja modules are in path
        for path in sys.path:
            if 'browser-ninja' in path:
                logger.debug("Detected browser-ninja context from sys.path")
                return 'browser-ninja'
        
        # Method 3: Check call stack for browser-ninja modules
        import inspect
        for frame_info in inspect.stack():
            if 'browser-ninja' in frame_info.filename:
                logger.debug("Detected browser-ninja context from call stack")
                return 'browser-ninja'
        
        # Method 4: Check environment variable (can be set explicitly)
        group = os.getenv('KAFKA_CONSUMER_GROUP')
        if group:
            logger.debug(f"Using explicit consumer group from env: {group}")
            return group
        
        # Default to autologin service consumer group
        logger.debug("Defaulting to auto-login-service consumer group")
        return 'auto-login-service'
    
    def _is_aws_environment(self) -> bool:
        """Check if running in AWS environment."""
        # Simple heuristics for AWS detection
        aws_indicators = [
            os.getenv('AWS_REGION'),
            os.getenv('AWS_DEFAULT_REGION'),
            Path('/opt/aws').exists(),
            os.getenv('EC2_INSTANCE_ID')
        ]
        return any(aws_indicators)
    
    def _get_kafka_servers(self) -> str:
        """Get Kafka bootstrap servers based on environment with flexible provider support."""
        # Priority 1: Explicit environment variable override
        env_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
        if env_servers:
            logger.debug(f"Using explicit KAFKA_BOOTSTRAP_SERVERS: {env_servers}")
            return env_servers
        
        # Priority 2: Provider-specific environment variables
        provider_servers = self._get_provider_servers()
        if provider_servers:
            return provider_servers
            
        # Priority 3: Environment-specific defaults
        servers_map = {
            'local': 'localhost:9092',
            'dev': self._get_dev_servers(),
            'stage': self._get_stage_servers(), 
            'prod': self._get_prod_servers()
        }
        
        servers = servers_map.get(self.environment, servers_map['local'])
        logger.debug(f"Using {self.environment} default servers: {servers}")
        return servers
    
    def _get_provider_servers(self) -> Optional[str]:
        """Get servers from provider-specific environment variables."""
        providers = {
            'MSK': os.getenv('KAFKA_MSK_SERVERS'),
            'CONFLUENT': os.getenv('KAFKA_CONFLUENT_SERVERS'), 
            'DOCKER': os.getenv('KAFKA_DOCKER_SERVERS'),
            'LOCAL': os.getenv('KAFKA_LOCAL_SERVERS')
        }
        
        for provider, servers in providers.items():
            if servers:
                logger.debug(f"Using {provider} servers: {servers}")
                return servers
        
        return None
    
    def _get_dev_servers(self) -> str:
        """Get dev environment Kafka servers."""
        # Support multiple dev configurations
        return os.getenv('KAFKA_DEV_SERVERS', 'kafka-dev:9092')
    
    def _get_stage_servers(self) -> str:
        """Get stage environment Kafka servers."""
        stage_servers = os.getenv('KAFKA_STAGE_SERVERS')
        if not stage_servers:
            logger.warning("KAFKA_STAGE_SERVERS not set - stage environment needs explicit configuration")
            logger.info("Example: export KAFKA_STAGE_SERVERS='stage-msk-1:9092,stage-msk-2:9092'")
            # Return local as fallback to prevent startup failure
            return 'localhost:9092'
        return stage_servers
    
    def _get_prod_servers(self) -> str:
        """Get production environment Kafka servers."""
        prod_servers = os.getenv('KAFKA_PROD_SERVERS')
        if not prod_servers:
            logger.error("KAFKA_PROD_SERVERS not set - production environment REQUIRES explicit configuration")
            logger.info("Example: export KAFKA_PROD_SERVERS='prod-msk-1:9092,prod-msk-2:9092,prod-msk-3:9092'")
            # Return local as fallback to prevent startup failure, but log error
            return 'localhost:9092'
        return prod_servers
    
    def _get_producer_settings(self) -> Dict[str, Any]:
        """Get producer settings optimized for environment."""
        base_settings = {
            'acks': 1,
            'retries': 10,
            'retry_backoff_ms': 1000,
            'request_timeout_ms': 60000,
            'delivery_timeout_ms': 120000,
            'linger_ms': 0,
            'batch_size': 16384,
            'buffer_memory': 33554432
        }
        
        if self.environment in ['stage', 'prod']:
            # MSK-optimized settings
            base_settings.update({
                'metadata_max_age_ms': 60000,
                'max_in_flight_requests_per_connection': 5,
                'request_timeout_ms': 60000
            })
        
        return base_settings
    
    def _get_consumer_settings(self) -> Dict[str, Any]:
        """Get consumer settings optimized for environment."""
        base_settings = {
            'auto_offset_reset': 'earliest',
            'enable_auto_commit': False,  # Manual commit for reliability
            'max_poll_records': 1,
            'consumer_timeout_ms': 5000
        }
        
        if self.environment in ['stage', 'prod']:
            # MSK-optimized settings  
            base_settings.update({
                'session_timeout_ms': 60000,
                'heartbeat_interval_ms': 20000,
                'max_poll_interval_ms': 300000,
                'request_timeout_ms': 70000,
                'api_version': (0, 10, 1)
            })
        else:
            # Local/dev settings
            base_settings.update({
                'session_timeout_ms': 30000,
                'heartbeat_interval_ms': 10000,
                'request_timeout_ms': 40000
            })
            
        return base_settings