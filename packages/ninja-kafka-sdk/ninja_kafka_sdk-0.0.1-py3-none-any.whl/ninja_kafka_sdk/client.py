"""
Main Ninja Kafka SDK client.
Provides simple interface for sending tasks to Ninja services and receiving results.
"""

import json
import logging
import asyncio
import threading
import time
from typing import Optional, Dict, Any, List, AsyncIterator, Callable, Union
from queue import Queue
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

from .config import NinjaKafkaConfig
from .models import NinjaTaskRequest, NinjaTaskResult, NinjaTaskProgress
from .exceptions import (
    NinjaKafkaError, NinjaKafkaConnectionError, 
    NinjaTaskTimeoutError, NinjaTaskError
)

logger = logging.getLogger(__name__)


class NinjaClient:
    """
    Main client for communicating with Ninja services via Kafka.
    
    Auto-detects environment and provides simple API for task execution.
    """
    
    def __init__(
        self,
        kafka_servers: Optional[str] = None,
        consumer_group: Optional[str] = None,
        environment: Optional[str] = None,
        timeout: int = 300,
        retry_attempts: int = 3,
        tasks_topic: str = 'ninja-tasks',
        results_topic: str = 'ninja-results',
        config: Optional[NinjaKafkaConfig] = None
    ):
        """
        Initialize Ninja client with explicit configuration.
        
        Args:
            kafka_servers: Kafka bootstrap servers (e.g., 'localhost:9092' or 'server1:9092,server2:9092')
            consumer_group: Consumer group for this client (auto-detected if None)
            environment: Environment name for logging (auto-detected if None)
            timeout: Default timeout for tasks in seconds
            retry_attempts: Number of retry attempts for failed operations
            tasks_topic: Kafka topic for sending tasks
            results_topic: Kafka topic for receiving results
            config: Custom configuration object (overrides other parameters)
        """
        if config:
            self.config = config
        else:
            self.config = NinjaKafkaConfig(
                kafka_servers=kafka_servers,
                consumer_group=consumer_group,
                environment=environment,
                tasks_topic=tasks_topic,
                results_topic=results_topic
            )
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.producer = None
        self.consumer = None
        self.consumer_thread = None
        self.task_consumer = None
        self.task_consumer_thread = None
        self._running = False
        self._results_queue = Queue()
        self._tasks_queue = Queue()
        self._pending_tasks = {}  # correlation_id -> task info
        
        logger.info(f"NinjaClient initialized (env: {self.config.environment})")
        logger.info(f"✅ Kafka configuration:")
        logger.info(f"   - Environment: {self.config.environment}")
        logger.info(f"   - Kafka servers: {self.config.kafka_servers}")
        logger.info(f"   - Tasks topic: {self.config.tasks_topic}")
        logger.info(f"   - Results topic: {self.config.results_topic}")
    
    async def send_task(
        self,
        task: str,
        account_id: int,
        email: Optional[str] = None,
        user_id: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send task to Ninja service.
        
        Args:
            task: Task type (e.g., 'linkedin_verification')
            account_id: Account ID
            email: Account email (optional)
            user_id: User ID (optional)
            **kwargs: Additional task parameters
            
        Returns:
            correlation_id: Unique ID to track this task
            
        Raises:
            NinjaKafkaConnectionError: If cannot connect to Kafka
            NinjaKafkaError: For other Kafka-related errors
        """
        if not self.producer:
            self._start_producer()
            
        # Start consumer to receive results if not already running
        if not self._running:
            self._start_consumer()
            
        # Create task request
        request = NinjaTaskRequest(
            task=task,
            account_id=account_id,
            email=email,
            user_id=user_id,
            metadata=kwargs
        )
        
        # Add API endpoints (following autologin pattern)
        if 'api_endpoints' not in request.metadata:
            request.api_endpoints = self._get_api_endpoints(account_id)
            
        # Track pending task
        self._pending_tasks[request.correlation_id] = {
            'request': request,
            'sent_at': time.time(),
            'status': 'pending'
        }
        
        try:
            # Send to Kafka (force partition 0 like autologin)
            future = self.producer.send(
                self.config.tasks_topic,
                value=request.to_dict(),
                key=f"task_{task}_account_{account_id}",
                partition=0
            )
            
            # Wait for send to complete
            result = future.get(timeout=30)
            
            logger.info(f"✅ Task sent successfully: {task} (correlation_id: {request.correlation_id[:8]})")
            logger.debug(f"Kafka result: topic={result.topic}, partition={result.partition}, offset={result.offset}")
            
            return request.correlation_id
            
        except KafkaError as e:
            # Check if this is a retryable partition leadership error
            retryable_errors = [
                'NotLeaderForPartitionError',
                'LeaderNotAvailableError',
                'RequestTimedOutError',
                'NetworkError'
            ]
            
            error_name = type(e).__name__
            if any(retryable in error_name for retryable in retryable_errors):
                logger.warning(f"⚠️ Retryable Kafka error ({error_name}), this is usually temporary")
                logger.warning(f"💡 MSK partition leadership is rebalancing - this should resolve automatically")
            
            # Remove from pending tasks on failure
            self._pending_tasks.pop(request.correlation_id, None)
            logger.error(f"❌ Failed to send task: {e}")
            raise NinjaKafkaConnectionError(f"Failed to send task: {e}") from e
    
    def send_task_sync(
        self,
        task: str,
        account_id: int,
        email: Optional[str] = None,
        user_id: Optional[int] = None,
        **kwargs
    ) -> str:
        """Synchronous version of send_task."""
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # We're in an async context, use thread executor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self._send_task_in_thread, task, account_id, email, user_id, **kwargs)
                return future.result(timeout=30)
        except RuntimeError:
            # No running loop, we can safely create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.send_task(task, account_id, email, user_id, **kwargs)
                )
            finally:
                loop.close()
    
    def _send_task_in_thread(self, task: str, account_id: int, email: Optional[str] = None, user_id: Optional[int] = None, **kwargs) -> str:
        """Helper method to run send_task in a separate thread with its own event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.send_task(task, account_id, email, user_id, **kwargs)
            )
        finally:
            loop.close()
    
    async def execute_task(
        self,
        task: str,
        account_id: int,
        timeout: Optional[int] = None,
        **kwargs
    ) -> NinjaTaskResult:
        """
        Send task and wait for result (high-level API).
        
        Args:
            task: Task type
            account_id: Account ID
            timeout: Timeout in seconds (uses default if None)
            **kwargs: Additional task parameters
            
        Returns:
            NinjaTaskResult: Task execution result
            
        Raises:
            NinjaTaskTimeoutError: If task times out
            NinjaTaskError: If task fails
        """
        timeout = timeout or self.timeout
        
        # Start consumer if not running
        if not self._running:
            self._start_consumer()
            
        # Send task
        correlation_id = await self.send_task(task, account_id, **kwargs)
        
        # Wait for result
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check for result
            if correlation_id in self._pending_tasks:
                task_info = self._pending_tasks[correlation_id]
                if task_info['status'] != 'pending':
                    result = task_info.get('result')
                    if result:
                        # Clean up
                        self._pending_tasks.pop(correlation_id, None)
                        
                        if result.is_success:
                            return result
                        else:
                            raise NinjaTaskError(
                                result.error_message or f"Task failed with status: {result.status}",
                                error_code=result.status,
                                details=result.error or {}
                            )
            
            # Brief sleep to avoid tight loop
            await asyncio.sleep(0.5)
        
        # Timeout
        self._pending_tasks.pop(correlation_id, None)
        raise NinjaTaskTimeoutError(f"Task {task} timed out after {timeout}s")
    
    def execute_task_sync(
        self,
        task: str,
        account_id: int,
        timeout: Optional[int] = None,
        **kwargs
    ) -> NinjaTaskResult:
        """Synchronous version of execute_task."""
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # We're in an async context, use thread executor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self._execute_task_in_thread, task, account_id, timeout, **kwargs)
                return future.result(timeout=(timeout or self.timeout) + 10)
        except RuntimeError:
            # No running loop, we can safely create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.execute_task(task, account_id, timeout, **kwargs)
                )
            finally:
                loop.close()
    
    def _execute_task_in_thread(self, task: str, account_id: int, timeout: Optional[int] = None, **kwargs) -> NinjaTaskResult:
        """Helper method to run execute_task in a separate thread with its own event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.execute_task(task, account_id, timeout, **kwargs)
            )
        finally:
            loop.close()
    
    async def listen_results(
        self,
        correlation_ids: Optional[List[str]] = None,
        handler: Optional[Callable[[NinjaTaskResult], None]] = None
    ) -> AsyncIterator[NinjaTaskResult]:
        """
        Listen for task results.
        
        Args:
            correlation_ids: Only yield results for these IDs (None = all)
            handler: Optional callback for each result
            
        Yields:
            NinjaTaskResult: Task results as they arrive
        """
        if not self._running:
            self._start_consumer()
            
        while self._running:
            try:
                # Check results queue
                if not self._results_queue.empty():
                    result = self._results_queue.get_nowait()
                    
                    # Filter by correlation_ids if specified
                    if correlation_ids and result.correlation_id not in correlation_ids:
                        continue
                        
                    # Call handler if provided
                    if handler:
                        try:
                            handler(result)
                        except Exception as e:
                            logger.error(f"Handler error: {e}")
                    
                    yield result
                else:
                    await asyncio.sleep(0.1)  # Brief pause if no results
                    
            except Exception as e:
                logger.error(f"Error in listen_results: {e}")
                await asyncio.sleep(1)
    
    async def listen_tasks(
        self,
        handler: Optional[Callable[[NinjaTaskRequest], None]] = None
    ) -> AsyncIterator[NinjaTaskRequest]:
        """
        Listen for incoming tasks (for Ninja services).
        
        Args:
            handler: Optional callback for each task
            
        Yields:
            NinjaTaskRequest: Task requests as they arrive
        """
        if not self._running:
            self._start_task_consumer()
            
        while self._running:
            try:
                # Check tasks queue  
                if hasattr(self, '_tasks_queue') and not self._tasks_queue.empty():
                    task = self._tasks_queue.get_nowait()
                    
                    # Call handler if provided
                    if handler:
                        try:
                            handler(task)
                        except Exception as e:
                            logger.error(f"Task handler error: {e}")
                    
                    yield task
                else:
                    await asyncio.sleep(0.1)  # Brief pause if no tasks
                    
            except Exception as e:
                logger.error(f"Error in listen_tasks: {e}")
                await asyncio.sleep(1)
    
    async def send_task_result(
        self,
        correlation_id: str,
        task: str,
        status: str,
        account_id: Optional[int] = None,
        verification_data: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send task result back to requesting service.
        
        Args:
            correlation_id: Request correlation ID
            task: Task type (e.g., 'linkedin_verification')  
            status: Status ('VERIFIED', 'FAILED', etc.)
            account_id: Account ID
            verification_data: Result data (cookies, etc.)
            error: Error details if failed
            metrics: Performance metrics
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.producer:
            self._start_producer()
            
        # Create result using our model
        result = NinjaTaskResult(
            correlation_id=correlation_id,
            task=task,
            status=status,
            account_id=account_id,
            success=status == 'VERIFIED',
            data=verification_data,
            error=error,
            metrics=metrics,
            cookies=verification_data.get('cookies') if verification_data else None
        )
        
        try:
            # Send to results topic - use working partition based on topic
            # Based on partition health testing (see simple_partition_tester.py):
            # ninja-results: partitions 1,3 work; 0,2 broken
            # ninja-tasks: partitions 0,2 work; 1,3 broken
            working_partition = self._get_working_partition(self.config.results_topic)
            
            future = self.producer.send(
                self.config.results_topic,
                value=result.__dict__,
                key=correlation_id,
                partition=working_partition
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=30)
            
            logger.info(f"✅ Task result sent: {task} ({correlation_id[:8]}) - {status}")
            logger.debug(f"Kafka result: topic={record_metadata.topic}, partition={record_metadata.partition}")
            
            return True
            
        except Exception as e:
            # Check if this is a retryable Kafka partition error
            error_str = str(e)
            retryable_patterns = [
                'NotLeaderForPartitionError',
                'LeaderNotAvailableError', 
                'RequestTimedOutError',
                'NetworkError'
            ]
            
            if any(pattern in error_str for pattern in retryable_patterns):
                logger.warning(f"⚠️ Retryable Kafka partition error: {e}")
                logger.warning(f"💡 This is usually temporary during MSK rebalancing")
                logger.warning(f"🔄 Task result will be lost - consider implementing retry logic in handlers")
            else:
                logger.error(f"❌ Non-retryable error sending task result: {e}")
            
            return False
    
    async def send_success_result(
        self,
        correlation_id: str,
        account_id: int,
        email: str,
        cookies: Optional[str] = None,
        screenshot: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send success result - compatibility with browser-ninja API.
        
        Args:
            correlation_id: Request correlation ID
            account_id: Account ID
            email: Account email
            cookies: Extracted cookies
            screenshot: Base64 screenshot
            details: Additional details
            
        Returns:
            True if sent successfully
        """
        verification_data = {
            'email': email,
            'cookies': cookies,
            'screenshot': screenshot
        }
        if details:
            verification_data.update(details)
            
        return await self.send_task_result(
            correlation_id=correlation_id,
            task='linkedin_verification',
            status='VERIFIED',
            account_id=account_id,
            verification_data=verification_data
        )
    
    async def send_error_result(
        self,
        correlation_id: str,
        account_id: Optional[int],
        email: Optional[str],
        error_code: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send error result - compatibility with browser-ninja API.
        
        Args:
            correlation_id: Request correlation ID
            account_id: Account ID if available
            email: Email if available  
            error_code: Error code
            error_message: Error message
            details: Additional error details
            
        Returns:
            True if sent successfully
        """
        verification_data = {'email': email} if email else None
        error_dict = {
            'code': error_code,
            'message': error_message
        }
        if details:
            error_dict.update(details)
            
        return await self.send_task_result(
            correlation_id=correlation_id,
            task='linkedin_verification',
            status='FAILED',
            account_id=account_id or 0,
            verification_data=verification_data,
            error=error_dict
        )
    
    def _get_working_partition(self, topic: str) -> int:
        """
        Get a working partition for the given topic.
        
        Based on partition health testing results:
        - ninja-results: partitions 1,3 work; 0,2 broken  
        - ninja-tasks: partitions 0,2 work; 1,3 broken
        
        This is a temporary workaround until partition leadership is fixed.
        """
        working_partitions = {
            'ninja-results': [1, 3],  # Primary: 1, Fallback: 3
            'ninja-tasks': [0, 2],    # Primary: 0, Fallback: 2
        }
        
        partitions = working_partitions.get(topic, [0])  # Default to partition 0
        return partitions[0]  # Use primary working partition
    
    def _start_producer(self):
        """Start Kafka producer."""
        try:
            # Convert comma-separated string to list if needed
            servers = self.config.kafka_servers
            if isinstance(servers, str):
                servers = [s.strip() for s in servers.split(',')]
            
            producer_settings = self.config.producer_settings
            logger.debug(f"Creating KafkaProducer with servers={servers}, settings={producer_settings}")
            
            self.producer = KafkaProducer(
                bootstrap_servers=servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                **producer_settings
            )
            logger.info(f"✅ Kafka producer started (servers: {self.config.kafka_servers})")
        except Exception as e:
            raise NinjaKafkaConnectionError(f"Failed to start producer: {e}") from e
    
    def _start_consumer(self):
        """Start Kafka consumer in background thread."""
        if self._running:
            return
            
        self._running = True
        self.consumer_thread = threading.Thread(target=self._consume_results, daemon=True)
        self.consumer_thread.start()
        logger.info("✅ Kafka consumer started in background thread")
    
    def _start_task_consumer(self):
        """Start Kafka task consumer in background thread (for Ninja services)."""
        if self._running:
            return
            
        self._running = True
        self.task_consumer_thread = threading.Thread(target=self._consume_tasks, daemon=True)
        self.task_consumer_thread.start()
        logger.info("✅ Kafka task consumer started in background thread")
    
    def _consume_results(self):
        """Consumer loop (runs in background thread)."""
        try:
            # Suppress kafka internal logging
            kafka_logger = logging.getLogger('kafka')
            original_level = kafka_logger.level
            kafka_logger.setLevel(logging.WARNING)
            
            # Convert comma-separated string to list if needed
            servers = self.config.kafka_servers
            if isinstance(servers, str):
                servers = [s.strip() for s in servers.split(',')]
            
            # Prepare consumer settings, avoiding duplicate keys
            consumer_settings = {
                'auto_offset_reset': 'earliest',
                'enable_auto_commit': True,
                'consumer_timeout_ms': 10000,
                'api_version_auto_timeout_ms': 10000,
                'max_poll_records': 1,
                # MSK-compatible settings
                'session_timeout_ms': 30000,
                'heartbeat_interval_ms': 10000,
                'max_poll_interval_ms': 300000,
                'request_timeout_ms': 40000,
            }
            
            # Update with config settings (config takes precedence)
            consumer_settings.update(self.config.consumer_settings)
            
            self.consumer = KafkaConsumer(
                self.config.results_topic,
                bootstrap_servers=servers,
                group_id=self.config.consumer_group,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                **consumer_settings
            )
            
            # Restore logging level
            kafka_logger.setLevel(original_level)
            
            logger.info(f"✅ Results consumer created successfully")
            logger.info(f"   Topic: {self.config.results_topic}")
            logger.info(f"   Bootstrap servers: {', '.join(servers)}")
            logger.info(f"   Consumer group: {self.config.consumer_group}")
            
            # Wait for partition assignment like task consumer
            logger.info("⏳ Waiting for results partition assignment...")
            assignment_timeout = time.time() + 15
            assigned = set()
            
            while time.time() < assignment_timeout and not assigned:
                self.consumer.poll(timeout_ms=1000)
                assigned = self.consumer.assignment()
                if assigned:
                    break
                logger.info(f"⏳ Still waiting for results partition assignment... ({int(15 - (assignment_timeout - time.time()))}s elapsed)")
            
            if assigned:
                logger.info(f"✅ Results partition assignment successful: {[f'{tp.topic}:{tp.partition}' for tp in assigned]}")
            else:
                logger.warning("❌ No results partitions assigned after 15 seconds")
            
            logger.info(f"📨 Results consumer loop started - waiting for messages...")
            
            # Health check variables
            last_poll_time = time.time()
            poll_count = 0
            result_count = 0
            
            # Consumer loop
            while self._running:
                try:
                    messages = self.consumer.poll(timeout_ms=1000)
                    poll_count += 1
                    
                    # Health check every 10 seconds
                    current_time = time.time()
                    if current_time - last_poll_time > 10:
                        logger.debug(f"🔄 Results consumer health: {poll_count} polls, {result_count} results in last 10s")
                        last_poll_time = current_time
                        poll_count = 0
                        result_count = 0
                    
                    for topic_partition, records in messages.items():
                        for record in records:
                            result_count += 1
                            try:
                                self._process_result(record.value)
                                # Commit after successful processing
                                self.consumer.commit()
                                logger.debug(f"✅ Result processed from {topic_partition.topic}:{topic_partition.partition}")
                            except Exception as e:
                                logger.error(f"Error processing result: {e}")
                                # Still commit to avoid reprocessing bad messages
                                self.consumer.commit()
                                
                except Exception as e:
                    if self._running:
                        logger.error(f"Consumer poll error: {e}")
                        time.sleep(2)
                        
        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            if self.consumer:
                self.consumer.close()
                logger.info("Consumer closed")
    
    def _consume_tasks(self):
        """Task consumer loop (runs in background thread for Ninja services)."""
        try:
            # Suppress kafka internal logging
            kafka_logger = logging.getLogger('kafka')
            original_level = kafka_logger.level
            kafka_logger.setLevel(logging.WARNING)
            
            # Convert comma-separated string to list if needed
            servers = self.config.kafka_servers
            if isinstance(servers, str):
                servers = [s.strip() for s in servers.split(',')]
            
            # Prepare consumer settings, avoiding duplicate keys
            consumer_settings = {
                'auto_offset_reset': 'earliest',
                'enable_auto_commit': True,
                'consumer_timeout_ms': 10000,
                'api_version_auto_timeout_ms': 10000,
                'max_poll_records': 1,
                # MSK-compatible settings for proper consumer group coordination
                'session_timeout_ms': 30000,
                'heartbeat_interval_ms': 10000,
                'max_poll_interval_ms': 300000,
                'request_timeout_ms': 40000,
            }
            
            # Update with config settings (config takes precedence)
            consumer_settings.update(self.config.consumer_settings)
            
            self.task_consumer = KafkaConsumer(
                self.config.tasks_topic,
                bootstrap_servers=servers,
                group_id=self.config.consumer_group,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                **consumer_settings
            )
            
            # Restore logging level
            kafka_logger.setLevel(original_level)
            
            logger.info(f"✅ Task consumer created successfully")
            logger.info(f"   Topic: {self.config.tasks_topic}")
            logger.info(f"   Bootstrap servers: {', '.join(servers)}")
            logger.info(f"   Consumer group: {self.config.consumer_group}")
            
            # Wait for partition assignment like original implementation
            logger.info("⏳ Waiting for partition assignment...")
            assignment_timeout = time.time() + 15
            assigned = set()
            
            while time.time() < assignment_timeout and not assigned:
                self.task_consumer.poll(timeout_ms=1000)
                assigned = self.task_consumer.assignment()
                if assigned:
                    break
                logger.info(f"⏳ Still waiting for partition assignment... ({int(15 - (assignment_timeout - time.time()))}s elapsed)")
            
            if assigned:
                logger.info(f"✅ Partition assignment successful after {int(15 - (assignment_timeout - time.time()))}s: {list(assigned)}")
                logger.info(f"📍 Assigned partitions: {[f'{tp.topic}:{tp.partition}' for tp in assigned]}")
                logger.info(f"🏷️  CONSUMER GROUP: {self.config.consumer_group}")
                logger.info("📊 Detailed offset information will be shown in periodic health checks")
            else:
                logger.error("❌ No partitions assigned after 15 seconds - consumer group coordination failed!")
                return
            
            logger.info(f"📨 Consumer loop started - waiting for messages...")
            logger.info(f"🏷️  CONSUMER GROUP: {self.config.consumer_group}")
            
            # Health check variables like original implementation
            last_poll_time = time.time()
            poll_count = 0
            message_count = 0
            
            # Consumer loop with detailed logging
            while self._running:
                try:
                    messages = self.task_consumer.poll(timeout_ms=100)
                    poll_count += 1
                    
                    # Enhanced health check every 10 seconds like original
                    current_time = time.time()
                    if current_time - last_poll_time > 10:
                        logger.info(f"🔄 Consumer health check (every 10s):")
                        logger.info(f"   📊 Last 10s: {poll_count} polls, {message_count} messages processed")
                        logger.info(f"   🏷️  CONSUMER GROUP: {self.config.consumer_group}")
                        
                        # Get partition assignment info
                        try:
                            assigned_partitions = self.task_consumer.assignment() if self.task_consumer else set()
                            logger.info(f"   📍 Assigned partitions ({len(assigned_partitions)}): {[f'{tp.topic}:{tp.partition}' for tp in assigned_partitions] if assigned_partitions else ['NONE']}")
                            logger.info(f"   ⏸️  Queue size: {self._tasks_queue.qsize()}")
                        except Exception as health_error:
                            logger.warning(f"   ❌ Health check failed: {str(health_error)[:100]}")
                        
                        last_poll_time = current_time
                        poll_count = 0
                        message_count = 0
                    
                    if messages:
                        for topic_partition, records in messages.items():
                            for record in records:
                                if not self._running:
                                    break
                                    
                                message_count += 1
                                try:
                                    task_data = record.value
                                    task = NinjaTaskRequest.from_dict(task_data)
                                    self._tasks_queue.put(task)
                                    
                                    logger.info(f"📩 Received message: {task.task_id} (consumer health: active)")
                                    logger.debug(f"✅ Task queued: {task.task_type} ({task.task_id[:8]})")
                                    
                                    # Commit after successful processing
                                    self.task_consumer.commit()
                                    
                                except Exception as e:
                                    logger.error(f"❌ Error processing task: {e}")
                                    # Still commit to avoid reprocessing bad messages
                                    self.task_consumer.commit()
                                    continue
                                
                except Exception as e:
                    if self._running:
                        logger.error(f"❌ Consumer poll error: {e}")
                        
                        # Recovery logic like original implementation
                        if "commit" in str(e).lower() or "timeout" in str(e).lower():
                            logger.warning("🔄 Detected commit/timeout error - attempting to recover consumer")
                            time.sleep(2)
                        else:
                            time.sleep(2)
                        
        except Exception as e:
            logger.error(f"Task consumer error: {e}")
        finally:
            if self.task_consumer:
                self.task_consumer.close()
                logger.info("Task consumer closed")
    
    def _process_result(self, raw_result: Dict[str, Any]):
        """Process incoming result message."""
        try:
            # Handle different message types
            if raw_result.get('type') == 'PROGRESS_UPDATE':
                progress = NinjaTaskProgress.from_dict(raw_result)
                logger.debug(f"Progress: {progress.status} - {progress.message}")
                return
                
            # Regular task result
            result = NinjaTaskResult.from_dict(raw_result)
            correlation_id = result.correlation_id
            
            # Comprehensive result logging for autologin
            logger.info(f"📥 AUTOLOGIN RECEIVED RESULT:")
            logger.info(f"   - Task: {result.task}")
            logger.info(f"   - Correlation ID: {correlation_id}")
            logger.info(f"   - Status: {result.status}")
            logger.info(f"   - Success: {result.is_success}")
            logger.info(f"   - Account ID: {result.account_id}")
            logger.info(f"   - Has cookies: {bool(result.cookies)}")
            logger.info(f"   - Has error: {bool(result.error)}")
            
            if result.error:
                logger.info(f"   - Error details: {result.error}")
            
            if result.cookies:
                logger.info(f"   - Cookies length: {len(result.cookies)} characters")
            
            logger.info(f"   - Raw result keys: {list(raw_result.keys())}")
            
            # Analyze success/failure for verification tasks
            if result.task == 'linkedin_verification':
                logger.info(f"🔍 LINKEDIN VERIFICATION ANALYSIS:")
                logger.info(f"   - SDK Success flag: {result.is_success}")
                logger.info(f"   - Status: {result.status}")
                logger.info(f"   - Error message: {result.error_message or 'None'}")
                
                # Check various success indicators
                has_cookies = bool(result.cookies and len(result.cookies.strip()) > 0)
                status_success = result.status in ['VERIFIED', 'SUCCESS', 'COMPLETED']
                explicit_success = result.is_success
                
                logger.info(f"   - Has valid cookies: {has_cookies}")
                logger.info(f"   - Status indicates success: {status_success}")
                logger.info(f"   - Explicit success flag: {explicit_success}")
                
                final_success = explicit_success or (status_success and has_cookies)
                logger.info(f"   - FINAL AUTOLOGIN SUCCESS: {final_success}")
                
                if not final_success:
                    logger.warning(f"❌ VERIFICATION FAILED - will not update cookies in database")
                else:
                    logger.info(f"✅ VERIFICATION SUCCESSFUL - will update cookies in database")
            
            # Update pending task
            if correlation_id in self._pending_tasks:
                self._pending_tasks[correlation_id]['status'] = 'completed'
                self._pending_tasks[correlation_id]['result'] = result
                logger.info(f"   - Updated pending task status to 'completed'")
            else:
                logger.warning(f"   - No pending task found for correlation_id {correlation_id}")
            
            # Add to results queue for async iteration
            self._results_queue.put(result)
            logger.info(f"   - Added result to queue for async processing")
            
        except Exception as e:
            logger.error(f"Error processing result: {e}")
    
    def _get_api_endpoints(self, account_id: int) -> Dict[str, str]:
        """Get API endpoints for inter-service communication (following autologin pattern)."""
        # Try to import service URLs helper
        try:
            from app.utils.service_urls import get_credentials_api_url, get_cookie_callback_api_url
            return {
                'credentials_url': get_credentials_api_url(account_id),
                'cookie_callback_url': get_cookie_callback_api_url(account_id, 'linkedin')
            }
        except ImportError:
            # Fallback to basic URLs (can be configured)
            base_url = "http://localhost:9000"  # Default autologin port
            return {
                'credentials_url': f"{base_url}/api/v1/localhost/credentials/{account_id}",
                'cookie_callback_url': f"{base_url}/api/v1/localhost/cookies/{account_id}/linkedin"
            }
    
    def stop(self):
        """Stop all Kafka connections."""
        logger.info("🛑 Stopping NinjaClient...")
        
        self._running = False
        
        if self.producer:
            try:
                self.producer.flush()
                self.producer.close()
                logger.info("Producer stopped")
            except Exception as e:
                logger.error(f"Error stopping producer: {e}")
        
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=5)
            logger.info("Consumer thread stopped")
        
        if self.task_consumer_thread and self.task_consumer_thread.is_alive():
            self.task_consumer_thread.join(timeout=5)
            logger.info("Task consumer thread stopped")
    
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()