# Ninja Kafka SDK

**Simple SDK for distributed task processing with Kafka messaging.**

Send tasks to Ninja services and get results back with just 3 lines of code instead of managing complex Kafka setup.

## 🚀 Quick Start - Send Your First Task

```python
from ninja_kafka_sdk import NinjaClient

# Configure your Kafka connection
client = NinjaClient(
    kafka_servers="your-kafka-servers:9092",
    consumer_group="your-service-name"
)

# Send task and wait for result
result = await client.execute_task(
    task="data_processing", 
    account_id=123,
    email="user@example.com"
)

if result.is_success:
    print("✅ Task completed successfully!")
    print(f"Result data: {result.data}")
else:
    print(f"❌ Failed: {result.error_message}")
```  

## 📦 Installation

```bash
# Copy to your project
cp -r ninja_kafka_sdk/ /your/project/

# Install dependencies (already in requirements.txt)
pip install kafka-python
```

## ⚙️ Configuration

### Explicit Configuration (Recommended)
```python
from ninja_kafka_sdk import NinjaClient

client = NinjaClient(
    kafka_servers="your-kafka-servers:9092",  # Change for your environment
    consumer_group="your-service-name"        # Unique name for your service
)
```

### Configuration from Variables
```python
import os
from ninja_kafka_sdk import NinjaClient

# Read from your application configuration
kafka_servers = os.getenv('MY_KAFKA_SERVERS', 'localhost:9092')
consumer_group = os.getenv('MY_CONSUMER_GROUP', 'my-service')

client = NinjaClient(
    kafka_servers=kafka_servers,
    consumer_group=consumer_group
)
```

### Configuration with Config Object
```python
from ninja_kafka_sdk import NinjaClient, NinjaKafkaConfig

# Create configuration object
config = NinjaKafkaConfig(
    kafka_servers="b-1.msk-cluster.amazonaws.com:9092,b-2.msk-cluster.amazonaws.com:9092",
    consumer_group="my-service",
    environment="stage",
    tasks_topic="ninja-tasks",
    results_topic="ninja-results"
)

# Use with client
client = NinjaClient(config=config)
```

### Auto-Detection Fallback
If no explicit configuration is provided, the SDK will attempt to auto-detect from:
1. Environment variables (`KAFKA_CONNECTION`)
2. Local configuration files (`app/local.py`)
3. AWS metadata (if running on EC2)
4. Smart defaults (`localhost:9092` for local development)

## 💡 How to Send Tasks

### Basic Task Execution
```python
from ninja_kafka_sdk import NinjaClient

async def verify_linkedin_account():
    # Explicit configuration for production
    client = NinjaClient(
        kafka_servers="b-1.msk-cluster.amazonaws.com:9092,b-2.msk-cluster.amazonaws.com:9092",
        consumer_group="auto-login-service",
        environment="prod"
    )
    
    try:
        # Send task and wait for result (one method call)
        result = await client.execute_task(
            task="linkedin_verification",
            account_id=12345,
            email="user@example.com",
            timeout=300  # 5 minutes
        )
        
        if result.is_success:
            print("✅ Verification successful!")
            return result.cookies
        else:
            print(f"❌ Failed: {result.error_message}")
            return None
            
    finally:
        client.stop()
```



### Advanced Usage Patterns

#### Fire and Forget
```python
async def send_multiple_tasks():
    client = NinjaClient()
    
    # Send task without waiting for result
    correlation_id = await client.send_task(
        task="linkedin_verification", 
        account_id=123
    )
    print(f"Task sent: {correlation_id}")
    client.stop()
```

#### Batch Processing
```python
async def process_multiple_accounts():
    client = NinjaClient()
    accounts = [123, 456, 789]

    try:
        # Send all tasks
        task_ids = []
        for account_id in accounts:
            task_id = await client.send_task("linkedin_verification", account_id=account_id)
            task_ids.append(task_id)

        # Listen for all results
        completed = 0
        async for result in client.listen_results(correlation_ids=task_ids):
            completed += 1
            print(f"Account {result.account_id}: {result.status}")
            if completed >= len(accounts):
                break
                
    finally:
        client.stop()
```

#### Synchronous Usage (Non-async Applications)
```python
def sync_verification():
    client = NinjaClient()

    try:
        # Synchronous task execution
        result = client.execute_task_sync(
            task="linkedin_verification",
            account_id=123,
            email="user@example.com",
            timeout=60
        )
        
        print(f"Result: {result.status}")
        return result.is_success
        
    finally:
        client.stop()
```

#### Environment-Specific Usage
```python
# Force specific environment
async def production_verification():
    # Explicitly use production configuration
    client = NinjaClient(environment="prod")
    
    # Will use KAFKA_PROD_SERVERS if set, otherwise shows warning
    result = await client.execute_task("linkedin_verification", account_id=123)
    client.stop()
    return result

# Auto-detect environment  
async def auto_verification():
    # Uses environment detection (local/dev/stage/prod)
    client = NinjaClient()
    result = await client.execute_task("linkedin_verification", account_id=123)
    client.stop()
    return result
```

## 🏗️ Available Tasks

### LinkedIn Verification
```python
result = await client.execute_task(
    task="linkedin_verification",
    account_id=123,
    email="user@example.com",  # Optional but highly recommended
    timeout=300  # 5 minutes
)
```

### Future Tasks
More task types will be added for different platforms:
- `twitter_verification`
- `instagram_verification` 
- `facebook_verification`

## 📝 Message Models

### Task Request
```python
@dataclass
class NinjaTaskRequest:
    task: str              # "linkedin_verification"
    account_id: int        # Account ID
    correlation_id: str    # Auto-generated UUID
    email: Optional[str]   # Account email
    user_id: Optional[int] # User ID
    metadata: Dict[str, Any]  # Additional parameters
```

### Task Result
```python
@dataclass 
class NinjaTaskResult:
    correlation_id: str    # Matches request
    task: str             # Task type
    status: str           # "VERIFIED", "FAILED", etc.
    success: bool         # True if successful
    account_id: int       # Account ID
    cookies: Optional[str] # Extracted cookies
    data: Optional[Dict]   # Additional result data
    error: Optional[Dict]  # Error details if failed
    
    @property
    def is_success(self) -> bool:
        return self.success or self.status == 'VERIFIED'
```

## 🚨 Error Handling

```python
from ninja_kafka_sdk import (
    NinjaClient, NinjaTaskTimeoutError, 
    NinjaTaskError, NinjaKafkaConnectionError
)

try:
    result = await client.execute_task("linkedin_verification", account_id=123)
    
except NinjaTaskTimeoutError:
    print("Task took too long")
    
except NinjaTaskError as e:
    print(f"Ninja couldn't complete task: {e.details}")
    
except NinjaKafkaConnectionError:
    print("Can't connect to Kafka")
```

## 🔌 Extending for New Services

```python
# Add new task types easily
await client.send_task(
    task="twitter_scraping",
    account_id=123,
    parameters={"target_user": "@elonmusk"}
)

# SDK handles routing to appropriate Ninja service
```



## 🔧 Troubleshooting

### Common Configuration Issues

#### Issue: "Can't connect to Kafka"
```python
# Check your servers configuration
from ninja_kafka_sdk.config import NinjaKafkaConfig
config = NinjaKafkaConfig()
print(f"Environment: {config.environment}")
print(f"Kafka servers: {config.kafka_servers}")
print(f"Consumer group: {config.consumer_group}")
```

**Solutions:**
1. **Local Development**: Ensure Kafka is running on `localhost:9092`
2. **Stage/Prod**: Verify `KAFKA_STAGE_SERVERS` or `KAFKA_PROD_SERVERS` are set
3. **Custom Provider**: Use `KAFKA_BOOTSTRAP_SERVERS` for explicit override

#### Issue: "No messages received"
```python
# Check consumer group conflicts
import os
print(f"Consumer group: {os.getenv('KAFKA_CONSUMER_GROUP', 'auto-detected')}")

# Force specific consumer group
os.environ['KAFKA_CONSUMER_GROUP'] = 'my-unique-group'
client = NinjaClient()
```

#### Issue: "Task timeout"
```python
# Increase timeout for slow operations
client = NinjaClient(timeout=600)  # 10 minutes
result = await client.execute_task("linkedin_verification", account_id=123, timeout=300)
```

### Environment Detection Debug

```python
from ninja_kafka_sdk.config import NinjaKafkaConfig

# Debug environment detection
config = NinjaKafkaConfig()
print(f"Environment: {config.environment}")
print(f"Servers: {config.kafka_servers}")

# Force specific environment
config = NinjaKafkaConfig(environment='stage')
print(f"Forced stage servers: {config.kafka_servers}")
```

### Quick Health Check

```python
from ninja_kafka_sdk import NinjaClient
import asyncio

async def health_check():
    client = NinjaClient()
    try:
        # Test connection by sending a test message
        correlation_id = await client.send_task("health_check", account_id=0)
        print(f"✅ Connection OK - Test message sent: {correlation_id}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    finally:
        client.stop()

# Run health check
asyncio.run(health_check())
```




---

## 📚 Appendix: For Service Implementers

This section contains information for developers implementing Ninja services (like browser-ninja) that process tasks and send results back.

### Sending Task Results

If you're building a service that processes Ninja tasks, use these methods to send results:

```python
from ninja_kafka_sdk import NinjaClient

async def send_verification_result():
    # Configure client for service that processes tasks
    client = NinjaClient(
        kafka_servers="your-kafka-servers:9092",
        consumer_group="browser-ninja",  # Service-specific consumer group
        environment="prod"
    )
    
    try:
        # Send success result
        await client.send_success_result(
            correlation_id="task-123-456",
            account_id=12345,
            email="user@example.com",
            cookies="extracted_cookies_data",
            screenshot="base64_screenshot"
        )
        
        # Or send error result
        await client.send_error_result(
            correlation_id="task-123-457",
            account_id=12346,
            email="user2@example.com",
            error_code="LOGIN_FAILED",
            error_message="Invalid credentials"
        )
        
    finally:
        client.stop()
```

### Listening for Tasks (Future Feature)

```python
from ninja_kafka_sdk import NinjaClient

async def process_ninja_tasks():
    client = NinjaClient(
        kafka_servers="your-kafka-servers:9092",
        consumer_group="browser-ninja"
    )
    
    try:
        # Listen for incoming tasks
        async for task in client.listen_tasks():
            print(f"📥 Received task: {task.task} for account {task.account_id}")
            
            # Process the task
            if task.task == "linkedin_verification":
                result = await process_linkedin_verification(task)
                
                # Send result back
                if result["success"]:
                    await client.send_success_result(
                        correlation_id=task.correlation_id,
                        account_id=task.account_id,
                        email=task.email,
                        cookies=result["cookies"]
                    )
                else:
                    await client.send_error_result(
                        correlation_id=task.correlation_id,
                        account_id=task.account_id,
                        email=task.email,
                        error_code=result["error_code"],
                        error_message=result["error_message"]
                    )
                    
    finally:
        client.stop()
```



---

**The Ninja Kafka SDK simplifies task-based communication while maintaining enterprise-grade reliability.**