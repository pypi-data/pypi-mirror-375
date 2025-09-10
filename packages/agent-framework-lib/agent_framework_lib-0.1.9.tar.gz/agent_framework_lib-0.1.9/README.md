# Agent Framework Library

A comprehensive Python framework for building and serving conversational AI agents with FastAPI. Features automatic multi-provider support (OpenAI, Gemini), dynamic configuration, session management, streaming responses, and a rich web interface.

**🎉 NEW: PyPI Package** - The Agent Framework is now available as a pip-installable package from PyPI, making it easy to integrate into any Python project.

## Installation

```bash
# Install from PyPI (recommended)
uv pip install agent-framework-lib

# Install with development dependencies
uv pip install agent-framework-lib[dev]

# Install from local source (development)
uv pip install -e .
```

## 🚀 Features

### Core Capabilities

- **Multi-Provider Support**: Automatic routing between OpenAI and Gemini APIs
- **Dynamic System Prompts**: Session-based system prompt control
- **Agent Configuration**: Runtime model parameter adjustment
- **Session Management**: Persistent conversation handling with structured workflow
- **Session Workflow**: Initialize/end session lifecycle with immutable configurations
- **User Feedback System**: Message-level thumbs up/down and session-level flags
- **Media Detection**: Automatic detection and handling of generated images/videos
- **Web Interface**: Built-in test application with rich UI controls
- **Debug Logging**: Comprehensive logging for system prompts and model configuration

### Advanced Features

- **Model Auto-Detection**: Automatic provider selection based on model name
- **Parameter Filtering**: Provider-specific parameter validation (e.g., Gemini doesn't support frequency_penalty)
- **Configuration Validation**: Built-in validation and status endpoints
- **Correlation & Conversation Tracking**: Link sessions across agents and track individual exchanges
- **Manager Agent Support**: Built-in coordination features for multi-agent workflows
- **Persistent Session Storage**: MongoDB integration for scalable session persistence (see [MongoDB Session Storage Guide](docs/mongodb_session_storage.md))
- **Agent Identity Support**: Multi-agent deployment support with automatic agent identification in MongoDB (see [Agent Identity Guide](docs/agent-identity-support.md))
- **File Storage System**: Persistent file management with multiple storage backends (Local, S3, MinIO) and intelligent routing (see [File Storage Implementation Guide](docs/file_storage_system_implementation.md))
- **Generated File Tracking**: Automatic distinction between user-uploaded and agent-generated files with comprehensive metadata
- **Multi-Storage Architecture**: Route different file types to appropriate storage systems with backend fallbacks
- **Markdown Conversion**: Automatic conversion of uploaded files (PDF, DOCX, TXT, etc.) to Markdown for optimal LLM processing with complete dependency support for all file types (see [Markdown Conversion Guide](docs/markdown_conversion_feature.md) and [Complete Fix Documentation](docs/markdown_conversion_fix_complete.md))
- **Reverse Proxy Support**: Automatic path prefix detection for deployment behind reverse proxies (see [Reverse Proxy Setup Guide](REVERSE_PROXY_SETUP.md))
- **Backward Compatibility**: Existing implementations continue to work

## 🚀 Quick Start

### Option 1: AutoGen-Based Agents (Recommended for AutoGen)

The fastest way to create AutoGen agents with all boilerplate handled automatically:

```python
from typing import Any, Dict, List
from agent_framework import AutoGenBasedAgent, create_basic_agent_server

class MyAgent(AutoGenBasedAgent):
    def get_agent_prompt(self) -> str:
        return "You are a helpful assistant that can perform calculations."
  
    def get_agent_tools(self) -> List[callable]:
        return [self.add, self.subtract]
  
    def get_agent_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Math Assistant",
            "description": "An agent that helps with basic math"
        }
  
    def create_autogen_agent(self, tools: List[callable], model_client: Any, system_message: str):
        """Create and configure the AutoGen agent."""
        from autogen_agentchat.agents import AssistantAgent
        return AssistantAgent(
            name="math_assistant",
            model_client=model_client,
            system_message=system_message,
            max_tool_iterations=250,
            reflect_on_tool_use=True,
            tools=tools,
            model_client_stream=True
        )
  
    @staticmethod
    def add(a: float, b: float) -> float:
        """Add two numbers together."""
        return a + b
  
    @staticmethod
    def subtract(a: float, b: float) -> float:
        """Subtract one number from another."""
        return a - b

# Start server with one line - includes AutoGen, MCP tools, streaming, etc.
create_basic_agent_server(MyAgent, port=8000)
```

**✨ Benefits:**

- **95% less code** - No AutoGen boilerplate needed
- **Built-in streaming** - Real-time responses with tool visualization
- **MCP integration** - Add external tools easily
- **Session management** - Automatic state persistence
- **10-15 minutes** to create a full-featured agent
- **Full control** over AutoGen agent type and configuration

### Option 2: Generic Agent Interface

For non-AutoGen agents or custom implementations:

```python
from agent_framework import AgentInterface, StructuredAgentInput, StructuredAgentOutput, create_basic_agent_server

class MyAgent(AgentInterface):
    async def get_metadata(self):
        return {"name": "My Agent", "version": "1.0.0"}
  
    async def handle_message(self, session_id: str, agent_input: StructuredAgentInput):
        return StructuredAgentOutput(response_text=f"Hello! You said: {agent_input.query}")

# Start server with one line - handles server setup, routing, and all framework features
create_basic_agent_server(MyAgent, port=8000)
```

See [docs/autogen_agent_guide.md](docs/autogen_agent_guide.md) for the complete AutoGen development guide.

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Configuration](#️-configuration)
- [API Reference](#-api-reference)
- [Client Examples](#-client-examples)
- [Web Interface](#-web-interface)
- [Advanced Usage](#-advanced-usage)
- [Development](#️-development)
- [AutoGen Development Guide](#-autogen-development-guide)
- [Authentication](#-authentication)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

## 🛠️ Development

### Traditional Development Setup

For development within the AgentFramework repository:

### 1. Installation

```bash
# Clone the repository
git clone <your-repository-url>
cd AgentFramework

# Install dependencies
uv venv
uv pip install -e .[dev]
```

### 2. Configuration

```bash
# Copy configuration template
cp env-template.txt .env

# Edit .env with your API keys
```

**Minimal .env setup:**

```env
# At least one API key required
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# Set default model
DEFAULT_MODEL=gpt-4

# Authentication (optional - set to true to enable)
REQUIRE_AUTH=false
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=password
API_KEYS=sk-your-secure-api-key-123
```

### 3. Start the Server

**Option A: Using convenience function (recommended for external projects)**

```python
# In your agent file
from agent_framework import create_basic_agent_server
create_basic_agent_server(MyAgent, port=8000)
```

**Option B: Traditional method**

```bash
# Start the development server
uv run python agent.py

# Or using uvicorn directly
export AGENT_CLASS_PATH="agent:Agent"
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test the Agent

Open your browser to `http://localhost:8000/ui` or make API calls:

```bash
# Without authentication (REQUIRE_AUTH=false)
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, how are you?"}'

# With API Key authentication (REQUIRE_AUTH=true)
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-your-secure-api-key-123" \
  -d '{"query": "Hello, how are you?"}'

# With Basic authentication (REQUIRE_AUTH=true)
curl -u admin:password -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, how are you?"}'
```

### Project Structure

```
AgentFramework/
├── agent_framework/             # Main framework package
│   ├── __init__.py             # Library exports and convenience functions
│   ├── agent_interface.py      # Abstract agent interface
│   ├── base_agent.py          # AutoGen-based agent implementation
│   ├── server.py              # FastAPI server
│   ├── model_config.py        # Multi-provider configuration
│   ├── model_clients.py       # Model client factory
│   └── session_storage.py     # Session storage implementations
├── examples/                   # Usage examples
├── docs/                      # Documentation
├── test_app.html             # Web interface
├── env-template.txt          # Configuration template
└── pyproject.toml           # Package configuration
```

### Creating Custom Agents

#### Option 1: AutoGen-Based Agents (Recommended)

For AutoGen-powered agents, inherit from `AutoGenBasedAgent` for maximum productivity:

```python
from typing import Any, Dict, List
from agent_framework import AutoGenBasedAgent, create_basic_agent_server

class MyAutoGenAgent(AutoGenBasedAgent):
    def get_agent_prompt(self) -> str:
        return """You are a specialized agent for [your domain].
        You can [list capabilities]."""
  
    def get_agent_tools(self) -> List[callable]:
        return [self.my_tool, self.another_tool]
  
    def get_agent_metadata(self) -> Dict[str, Any]:
        return {
            "name": "My AutoGen Agent",
            "description": "A specialized agent with AutoGen superpowers",
            "capabilities": {
                "streaming": True,
                "tool_use": True,
                "mcp_integration": True
            }
        }
  
    def create_autogen_agent(self, tools: List[callable], model_client: Any, system_message: str):
        """Create and configure the AutoGen agent."""
        from autogen_agentchat.agents import AssistantAgent
        return AssistantAgent(
            name="my_agent",
            model_client=model_client,
            system_message=system_message,
            max_tool_iterations=300,
            reflect_on_tool_use=True,
            tools=tools,
            model_client_stream=True
        )
  
    @staticmethod
    def my_tool(input_data: str) -> str:
        """Your custom tool implementation."""
        return f"Processed: {input_data}"

# Start server with full AutoGen capabilities
create_basic_agent_server(MyAutoGenAgent, port=8000)
```

**✨ What you get automatically:**

- Real-time streaming responses
- MCP tools integration
- Session state management
- Tool call visualization
- Error handling & logging
- Special block parsing (forms, charts, etc.)

#### Option 2: Generic AgentInterface

For non-AutoGen agents or when you need full control:

```python
from agent_framework import AgentInterface, StructuredAgentInput, StructuredAgentOutput

class MyCustomAgent(AgentInterface):
    async def handle_message(self, session_id: str, agent_input: StructuredAgentInput) -> StructuredAgentOutput:
        # Implement your logic here
        pass
  
    async def handle_message_stream(self, session_id: str, agent_input: StructuredAgentInput):
        # Implement streaming logic
        pass
  
    async def get_metadata(self):
        return {
            "name": "My Custom Agent",
            "description": "A custom agent implementation",
            "capabilities": {"streaming": True}
        }
  
    def get_system_prompt(self) -> Optional[str]:
        return "Your custom system prompt here..."

# Start server
create_basic_agent_server(MyCustomAgent, port=8000)
```

### Testing

The project includes a comprehensive test suite built with `pytest` and optimized for UV-based testing. The tests are located in the `tests/` directory and are configured to run in a self-contained environment with multiple test categories.

**🚀 Quick Start with UV (Recommended):**

```bash
# Install test dependencies
uv sync --group test

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=agent_framework --cov-report=html

# Run specific test types
uv run pytest -m unit          # Fast unit tests
uv run pytest -m integration   # Integration tests
uv run pytest -m "not slow"    # Skip slow tests
```

**📚 Comprehensive Testing Guide:**

For detailed instructions on UV-based testing, test categories, CI/CD integration, and development workflows, see:

[**UV Testing Guide**](docs/UV_TESTING_GUIDE.md)

**🛠️ Alternative Methods:**

```bash
# Using Make (cross-platform)
make test                    # Run all tests
make test-coverage          # Run with coverage
make test-fast              # Run fast tests only

# Using test scripts
./scripts/test.sh coverage  # Unix/macOS
scripts\test.bat coverage   # Windows

# Using Python test runner
python scripts/test_runner.py --install-deps coverage
```

**📊 Test Categories:**

- `unit` - Fast, isolated component tests
- `integration` - Multi-component workflow tests  
- `performance` - Benchmark and performance tests
- `multimodal` - Tests requiring AI vision/audio capabilities
- `storage` - File storage backend tests
- `slow` - Long-running tests (excluded from fast runs)

### Debug Logging

Set debug logging to see detailed system prompt and configuration information:

```bash
export AGENT_LOG_LEVEL=DEBUG
uv run python agent.py
```

Debug logs include:

- Model configuration loading and validation
- System prompt handling and persistence
- Agent configuration merging and application
- Provider selection and parameter filtering
- Client creation and model routing

## ⚙️ Configuration

### Session Storage Configuration

Configure persistent session storage (optional):

```env
# === Session Storage ===
# Use "memory" (default) for in-memory storage or "mongodb" for persistent storage
SESSION_STORAGE_TYPE=memory

# MongoDB configuration (only required when SESSION_STORAGE_TYPE=mongodb)
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE_NAME=agent_sessions
MONGODB_COLLECTION_NAME=sessions
```

For detailed MongoDB setup and configuration, see the [MongoDB Session Storage Guide](docs/mongodb_session_storage.md).

## 📚 API Reference

### Core Endpoints

#### Send Message

Send a message to the agent and receive a complete response.

**Endpoint:** `POST /message`

**Request Body:**

```json
{
  "query": "Your message here",
  "parts": [],
  "system_prompt": "Optional custom system prompt",
  "agent_config": {
    "temperature": 0.8,
    "max_tokens": 1000,
    "model_selection": "gpt-4"
  },
  "session_id": "optional-session-id",
  "correlation_id": "optional-correlation-id-for-linking-sessions"
}
```

**Response:**

```json
{
  "response_text": "Agent's response",
  "parts": [
    {
      "type": "text",
      "text": "Agent's response"
    }
  ],
  "session_id": "generated-or-provided-session-id",
  "user_id": "user1",
  "correlation_id": "correlation-id-if-provided",
  "conversation_id": "unique-id-for-this-exchange"
}
```

#### Session Workflow (NEW)

**Initialize Session:** `POST /init`

```json
{
  "user_id": "string",           // required
  "correlation_id": "string",    // optional
  "session_id": "string",        // optional (auto-generated if not provided)
  "data": { ... },               // optional
  "configuration": {             // required
    "system_prompt": "string",
    "model_name": "string",
    "model_config": {
      "temperature": 0.7,
      "token_limit": 1000
    }
  }
}
```

Initializes a new chat session with immutable configuration. Must be called before any chat interactions. Returns the session configuration and generated session ID if not provided.

**End Session:** `POST /end`

```json
{
  "session_id": "string"
}
```

Closes a session and prevents further interactions. Persists final session state and locks feedback system.

**Submit Message Feedback:** `POST /feedback/message`

```json
{
  "session_id": "string",
  "message_id": "string",
  "feedback": "up" | "down"
}
```

Submit thumbs up/down feedback for a specific message. Can only be submitted once per message.

**Submit/Update Session Flag:** `POST|PUT /feedback/flag`

```json
{
  "session_id": "string",
  "flag_message": "string"
}
```

Submit or update a session-level flag message. Editable while session is active, locked after session ends.

#### Session Management

**List Sessions:** `GET /sessions`

```bash
curl http://localhost:8000/sessions
# Response: ["session1", "session2", ...]
```

**Get History:** `GET /sessions/{session_id}/history`

```bash
curl http://localhost:8000/sessions/abc123/history
```

**Find Sessions by Correlation ID:** `GET /sessions/by-correlation/{correlation_id}`

```bash
curl http://localhost:8000/sessions/by-correlation/task-123
# Response: [{"user_id": "user1", "session_id": "abc123", "correlation_id": "task-123"}]
```

### Correlation & Conversation Tracking

The framework provides advanced tracking capabilities for multi-agent workflows and detailed conversation analytics.

#### Correlation ID Support

**Purpose**: Link multiple sessions across different agents that are part of the same larger task or workflow.

**Usage**:

```python
# Start a task with correlation ID
response1 = client.send_message(
    "Analyze this data set",
    correlation_id="data-analysis-task-001"
)

# Continue task in another session/agent with same correlation ID
response2 = client.send_message(
    "Generate visualizations for the analysis",
    correlation_id="data-analysis-task-001"  # Same correlation ID
)

# Find all sessions related to this task
sessions = requests.get("/sessions/by-correlation/data-analysis-task-001")
```

**Key Features**:

- **Optional field**: Can be set when sending messages or creating sessions
- **Persistent**: Correlation ID is maintained throughout the session lifecycle
- **Cross-agent**: Multiple agents can share the same correlation ID
- **Searchable**: Query all sessions by correlation ID

#### Conversation ID Support

**Purpose**: Track individual message exchanges (request/reply pairs) within sessions for detailed analytics and debugging.

**Key Features**:

- **Automatic generation**: Each request/reply pair gets a unique conversation ID
- **Shared between request/reply**: User message and agent response share the same conversation ID
- **Database-ready**: Designed for storing individual exchanges in databases
- **Analytics-friendly**: Enables detailed conversation flow analysis

**Example Response with IDs**:

```json
{
  "response_text": "Here's the analysis...",
  "session_id": "session-abc-123",
  "user_id": "data-scientist-1",
  "correlation_id": "data-analysis-task-001",
  "conversation_id": "conv-uuid-456-789"
}
```

#### Manager Agent Coordination

These features enable sophisticated multi-agent workflows:

```python
class ManagerAgent:
    def __init__(self):
        self.correlation_id = f"task-{uuid.uuid4()}"
  
    async def coordinate_task(self, task_description):
        # Step 1: Data analysis agent
        analysis_response = await self.send_to_agent(
            "data-agent", 
            f"Analyze: {task_description}",
            correlation_id=self.correlation_id
        )
    
        # Step 2: Visualization agent
        viz_response = await self.send_to_agent(
            "viz-agent",
            f"Create charts for: {analysis_response}",
            correlation_id=self.correlation_id
        )
    
        # Step 3: Find all related sessions
        related_sessions = await self.get_sessions_by_correlation(self.correlation_id)
    
        return {
            "task_id": self.correlation_id,
            "sessions": related_sessions,
            "final_result": viz_response
        }
```

#### Web Interface Features

The test application includes full support for correlation tracking:

- **Correlation ID Input**: Set correlation IDs when sending messages
- **Session Finder**: Search for all sessions sharing a correlation ID
- **ID Display**: Shows correlation and conversation IDs in chat history
- **Visual Indicators**: Clear display of tracking information

#### Configuration Endpoints

**Get Model Configuration:** `GET /config/models`

```json
{
  "default_model": "gpt-4",
  "configuration_status": {
    "valid": true,
    "warnings": [],
    "errors": []
  },
  "supported_models": {
    "openai": ["gpt-4", "gpt-3.5-turbo"],
    "gemini": ["gemini-1.5-pro", "gemini-pro"]
  },
  "supported_providers": {
    "openai": true,
    "gemini": true
  }
}
```

**Validate Model:** `GET /config/validate/{model_name}`

```json
{
  "model": "gpt-4",
  "provider": "openai",
  "supported": true,
  "api_key_configured": true,
  "client_available": true,
  "issues": []
}
```

**Get System Prompt:** `GET /system-prompt`

```json
{
  "system_prompt": "You are a helpful AI assistant that helps users accomplish their tasks efficiently..."
}
```

Returns the default system prompt configured for the agent. Returns 404 if no system prompt is configured.

**Response (404 if not configured):**

```json
{
  "detail": "System prompt not configured"
}
```

### Agent Configuration Parameters

| Parameter             | Type    | Range    | Description                | Providers      |
| --------------------- | ------- | -------- | -------------------------- | -------------- |
| `temperature`       | float   | 0.0-2.0  | Controls randomness        | OpenAI, Gemini |
| `max_tokens`        | integer | 1+       | Maximum response tokens    | OpenAI, Gemini |
| `top_p`             | float   | 0.0-1.0  | Nucleus sampling           | OpenAI, Gemini |
| `frequency_penalty` | float   | -2.0-2.0 | Reduce frequent tokens     | OpenAI only    |
| `presence_penalty`  | float   | -2.0-2.0 | Reduce any repetition      | OpenAI only    |
| `stop_sequences`    | array   | -        | Custom stop sequences      | OpenAI, Gemini |
| `timeout`           | integer | 1+       | Request timeout (seconds)  | OpenAI, Gemini |
| `max_retries`       | integer | 0+       | Retry attempts             | OpenAI, Gemini |

#### File Storage Endpoints

The framework includes a comprehensive file storage system with support for multiple backends (Local, S3, MinIO) and automatic file management.

**Upload File:** `POST /files/upload`

```bash
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer your-token" \
  -F "file=@example.pdf" \
  -F "user_id=user-123" \
  -F "session_id=session-123"
```

**Response:**
```json
{
  "file_id": "uuid-here",
  "filename": "example.pdf",
  "size_bytes": 12345,
  "mime_type": "application/pdf"
}
```

**Download File:** `GET /files/{file_id}/download`

```bash
curl -X GET "http://localhost:8000/files/{file_id}/download" \
  -H "Authorization: Bearer your-token" \
  -o downloaded_file.pdf
```

**Get File Metadata:** `GET /files/{file_id}/metadata`

```json
{
  "file_id": "uuid-here",
  "filename": "example.pdf",
  "mime_type": "application/pdf",
  "size_bytes": 12345,
  "created_at": "2025-07-28T12:37:33Z",
  "updated_at": "2025-07-28T12:37:33Z",
  "user_id": "user-123",
  "session_id": "session-123",
  "agent_id": null,
  "is_generated": false,
  "tags": [],
  "storage_backend": "local"
}
```

**List Files:** `GET /files?user_id=user-123&session_id=session-123&is_generated=false`

**Delete File:** `DELETE /files/{file_id}`

**Storage Statistics:** `GET /files/stats`

```json
{
  "backends": ["local", "s3"],
  "default_backend": "local",
  "routing_rules": {
    "image/": "s3",
    "video/": "s3"
  }
}
```

**File Storage Configuration:**

The file storage system supports environment-based configuration for multiple backends:

```bash
# Local Storage (always enabled)
LOCAL_STORAGE_PATH=./file_storage

# AWS S3 (optional)
AWS_S3_BUCKET=my-agent-files
AWS_REGION=us-east-1
S3_AS_DEFAULT=false

# MinIO (optional)  
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=agent-files

# Routing Rules
IMAGE_STORAGE_BACKEND=s3
VIDEO_STORAGE_BACKEND=s3
FILE_ROUTING_RULES=image/:s3,video/:minio
```

**Key Features:**
- **Multi-Backend Support**: Local, S3, and MinIO storage backends
- **Intelligent Routing**: Route files to appropriate backends based on MIME type
- **Generated File Tracking**: Automatic distinction between uploaded and agent-generated files
- **Comprehensive Metadata**: Full file lifecycle tracking with user/session associations
- **Backward Compatibility**: Existing file handling continues to work seamlessly

For detailed configuration and usage examples, see the [File Storage Implementation Guide](docs/file_storage_system_implementation.md).
| `model_selection`   | string  | -        | Override model for session | OpenAI, Gemini |

## 💻 Client Examples

### Python Client

```python
import requests
import json

class AgentClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        # Add basic auth if required
        self.session.auth = ("admin", "password")
  
    def send_message(self, message, session_id=None, correlation_id=None):
        """Send a message and get complete response."""
        payload = {
            "query": message,
            "parts": []
        }
    
        if session_id:
            payload["session_id"] = session_id
        if correlation_id:
            payload["correlation_id"] = correlation_id
    
        response = self.session.post(
            f"{self.base_url}/message",
            json=payload
        )
        response.raise_for_status()
        return response.json()
  
    def init_session(self, user_id, configuration, correlation_id=None, session_id=None, data=None):
        """Initialize a new session with configuration."""
        payload = {
            "user_id": user_id,
            "configuration": configuration
        }
    
        if correlation_id:
            payload["correlation_id"] = correlation_id
        if session_id:
            payload["session_id"] = session_id
        if data:
            payload["data"] = data
    
        response = self.session.post(
            f"{self.base_url}/init",
            json=payload
        )
        response.raise_for_status()
        return response.json()
  
    def end_session(self, session_id):
        """End a session."""
        response = self.session.post(
            f"{self.base_url}/end",
            json={"session_id": session_id}
        )
        response.raise_for_status()
        return response.ok
  
    def submit_feedback(self, session_id, message_id, feedback):
        """Submit feedback for a message."""
        response = self.session.post(
            f"{self.base_url}/feedback/message",
            json={
                "session_id": session_id,
                "message_id": message_id,
                "feedback": feedback
            }
        )
        response.raise_for_status()
        return response.ok
  
    def get_model_config(self):
        """Get available models and configuration."""
        response = self.session.get(f"{self.base_url}/config/models")
        response.raise_for_status()
        return response.json()

# Usage example
client = AgentClient()

# Initialize session with configuration
session_data = client.init_session(
    user_id="user123",
    configuration={
        "system_prompt": "You are a creative writing assistant",
        "model_name": "gpt-4",
        "model_config": {
            "temperature": 1.2,
            "token_limit": 500
        }
    },
    correlation_id="creative-writing-session-001"
)

session_id = session_data["session_id"]

# Send messages using the initialized session
response = client.send_message(
    "Write a creative story about space exploration",
    session_id=session_id
)
print(response["response_text"])

# Submit feedback on the response
client.submit_feedback(session_id, response["conversation_id"], "up")

# Continue the conversation
response2 = client.send_message("Add more details about the characters", session_id=session_id)
print(response2["response_text"])

# End session when done
client.end_session(session_id)
```

### JavaScript Client

```javascript
class AgentClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.auth = btoa('admin:password'); // Basic auth
    }
  
    async sendMessage(message, options = {}) {
        const payload = {
            query: message,
            parts: [],
            ...options
        };
    
        const response = await fetch(`${this.baseUrl}/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Basic ${this.auth}`
            },
            body: JSON.stringify(payload)
        });
    
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    
        return response.json();
    }
  
    async initSession(userId, configuration, options = {}) {
        const payload = {
            user_id: userId,
            configuration,
            ...options
        };
    
        const response = await fetch(`${this.baseUrl}/init`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Basic ${this.auth}`
            },
            body: JSON.stringify(payload)
        });
    
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    
        return response.json();
    }
  
    async endSession(sessionId) {
        const response = await fetch(`${this.baseUrl}/end`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Basic ${this.auth}`
            },
            body: JSON.stringify({ session_id: sessionId })
        });
    
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    
        return response.ok;
    }
  
    async submitFeedback(sessionId, messageId, feedback) {
        const response = await fetch(`${this.baseUrl}/feedback/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Basic ${this.auth}`
            },
            body: JSON.stringify({
                session_id: sessionId,
                message_id: messageId,
                feedback
            })
        });
    
        return response.ok;
    }
  
    async getModelConfig() {
        const response = await fetch(`${this.baseUrl}/config/models`, {
            headers: { 'Authorization': `Basic ${this.auth}` }
        });
        return response.json();
    }
}

// Usage example
const client = new AgentClient();

// Initialize session with configuration
const sessionInit = await client.initSession('user123', {
    system_prompt: 'You are a helpful coding assistant',
    model_name: 'gpt-4',
    model_config: {
        temperature: 0.7,
        token_limit: 1000
    }
}, {
    correlation_id: 'coding-help-001'
});

// Send messages using the initialized session
const response = await client.sendMessage('Help me debug this Python code', {
    session_id: sessionInit.session_id
});
console.log(response.response_text);

// Submit feedback
await client.submitFeedback(sessionInit.session_id, response.conversation_id, 'up');

// End session when done
await client.endSession(sessionInit.session_id);
```

### curl Examples

```bash
# Basic message with correlation ID
curl -X POST http://localhost:8000/message \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Hello, world!",
    "correlation_id": "greeting-task-001",
    "agent_config": {
      "temperature": 0.8,
      "model_selection": "gpt-4"
    }
  }'

# Initialize session
curl -X POST http://localhost:8000/init \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "correlation_id": "poetry-session-001",
    "configuration": {
      "system_prompt": "You are a talented poet",
      "model_name": "gpt-4",
      "model_config": {
        "temperature": 1.5,
        "token_limit": 200
      }
    }
  }'

# Submit feedback for a message
curl -X POST http://localhost:8000/feedback/message \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123",
    "message_id": "msg-456",
    "feedback": "up"
  }'

# End session
curl -X POST http://localhost:8000/end \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123"
  }'

# Get model configuration
curl http://localhost:8000/config/models -u admin:password

# Validate model support
curl http://localhost:8000/config/validate/gemini-1.5-pro -u admin:password

# Get system prompt
curl http://localhost:8000/system-prompt -u admin:password

# Find sessions by correlation ID
curl http://localhost:8000/sessions/by-correlation/greeting-task-001 -u admin:password
```

## 🌐 Web Interface

- TODO

## 🔧 Advanced Usage

### System Prompt Configuration

The framework supports configurable system prompts both at the server level and per-session:

#### Server-Level System Prompt

Agents can provide a default system prompt via the `get_system_prompt()` method:

```python
class MyAgent(AgentInterface):
    def get_system_prompt(self) -> Optional[str]:
        return """
        You are a helpful coding assistant specializing in Python.
        Always provide:
        1. Working code examples
        2. Clear explanations
        3. Best practices
        4. Error handling
        """
```

#### Accessing System Prompt via API

```python
# Get the default system prompt from server
response = requests.get("http://localhost:8000/system-prompt")
if response.status_code == 200:
    system_prompt = response.json()["system_prompt"]
else:
    print("No system prompt configured")
```

#### Per-Session System Prompts

```python
# Set system prompt for specific use case
custom_prompt = """
You are a creative writing assistant.
Focus on storytelling and narrative structure.
"""

response = client.send_message(
    "Help me write a short story",
    system_prompt=custom_prompt
)
```

#### Web Interface System Prompt Management

The web interface provides comprehensive system prompt management:

- **Auto-loading**: Default system prompt loads automatically on new sessions
- **Session persistence**: Each session remembers its custom system prompt
- **Reset functionality**: "🔄 Reset to Default" button restores server default
- **Manual reload**: Refresh system prompt from server without losing session data

## 🤖 AutoGen Development Guide

The Agent Framework provides a comprehensive base class for AutoGen agents that eliminates 95% of boilerplate code. This allows you to focus on your agent's specific logic rather than AutoGen integration details.

### Quick Start with AutoGen

```python
from typing import Any, Dict, List
from agent_framework import AutoGenBasedAgent, create_basic_agent_server

class DataAnalysisAgent(AutoGenBasedAgent):
    def get_agent_prompt(self) -> str:
        return """You are a data analysis expert.
        You can analyze datasets, create visualizations, and generate insights.
        Always provide clear explanations and cite your sources."""
  
    def get_agent_tools(self) -> List[callable]:
        return [self.analyze_data, self.create_chart, self.summarize_findings]
  
    def get_agent_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Data Analysis Agent",
            "description": "Expert in statistical analysis and data visualization",
            "version": "1.0.0",
            "capabilities": {
                "data_analysis": True,
                "visualization": True,
                "statistical_modeling": True
            }
        }
  
    def create_autogen_agent(self, tools: List[callable], model_client: Any, system_message: str):
        """Create an AssistantAgent optimized for data analysis."""
        from autogen_agentchat.agents import AssistantAgent
        return AssistantAgent(
            name="data_analyst",
            model_client=model_client,
            system_message=system_message,
            max_tool_iterations=400,  # More iterations for complex analysis
            reflect_on_tool_use=True,
            tools=tools,
            model_client_stream=True
        )
  
    @staticmethod
    def analyze_data(dataset: str, analysis_type: str = "descriptive") -> str:
        """Analyze a dataset with specified analysis type."""
        # Your data analysis logic here
        return f"Analysis complete for {dataset} using {analysis_type} methods"
  
    @staticmethod  
    def create_chart(data: str, chart_type: str = "bar") -> str:
        """Create a chart from data."""
        # Return chart configuration
        return f'```chart\n{{"type": "chartjs", "chartConfig": {{"type": "{chart_type}"}}}}\n```'

# Start server - includes AutoGen, streaming, MCP tools, state management
create_basic_agent_server(DataAnalysisAgent, port=8000)
```

### What AutoGenBasedAgent Provides

**✅ Complete AutoGen Integration:**

- AssistantAgent setup and lifecycle management
- Model client factory integration
- AutoGen agent configuration

**✅ Advanced Features:**

- Real-time streaming with event handling
- MCP (Model Context Protocol) tools integration
- Session management and state persistence
- Special block parsing (forms, charts, tables, options)
- Tool call visualization and debugging

**✅ Error Handling:**

- Robust error handling and logging
- Graceful degradation for failed components
- Comprehensive debugging information

### Adding MCP Tools

```python
from autogen_ext.tools.mcp import StdioServerParams

class AdvancedAgent(AutoGenBasedAgent):
    # ... implement required methods ...
  
    def get_mcp_server_params(self) -> List[StdioServerParams]:
        """Configure external MCP tools."""
        return [
            # Python execution server
            StdioServerParams(
                command='deno',
                args=['run', '-N', '-R=node_modules', '-W=node_modules',
                      '--node-modules-dir=auto', 'jsr:@pydantic/mcp-run-python', 'stdio'],
                read_timeout_seconds=120
            ),
            # File system access server
            StdioServerParams(
                command='npx',
                args=['-y', '@modelcontextprotocol/server-filesystem', '/tmp'],
                read_timeout_seconds=60
            )
        ]
```

### Development Benefits

**📉 95% Code Reduction:**

- **Before**: 970+ lines of boilerplate per agent
- **After**: 40-60 lines for a complete agent

**⚡ Faster Development:**

- **Before**: 2-3 hours to create new agent
- **After**: 10-15 minutes to create new agent

**🔧 Better Maintainability:**

- Framework updates benefit all agents automatically
- Consistent behavior across all AutoGen agents
- Single source of truth for AutoGen integration

### Complete Documentation

For comprehensive documentation, examples, and best practices, see:

- **[AutoGen Agent Development Guide](docs/autogen_agent_guide.md)** - Complete tutorial with examples
- **[AutoGen Refactoring Summary](docs/autogen_refactoring_summary.md)** - Architecture and benefits overview

### Model-Specific Configuration

```python
# OpenAI-specific configuration
openai_config = {
    "model_selection": "gpt-4",
    "temperature": 0.7,
    "frequency_penalty": 0.5,  # OpenAI only
    "presence_penalty": 0.3    # OpenAI only
}

# Gemini-specific configuration  
gemini_config = {
    "model_selection": "gemini-1.5-pro",
    "temperature": 0.8,
    "top_p": 0.9,
    "max_tokens": 1000
    # Note: frequency_penalty not supported by Gemini
}
```

### Session Persistence

```python
# Start conversation with custom settings
response1 = client.send_message(
    "Let's start a coding session",
    system_prompt="You are my coding pair programming partner",
    config={"temperature": 0.3}
)

session_id = response1["session_id"]

# Continue conversation - settings persist
response2 = client.send_message(
    "Help me debug this function",
    session_id=session_id
)

# Override settings for this message only
response3 = client.send_message(
    "Now be creative and suggest alternatives", 
    session_id=session_id,
    config={"temperature": 1.5}  # Temporary override
)
```

### Multi-Modal Support

```python
# Send image with message
payload = {
    "query": "What's in this image?",
    "parts": [
        {
            "type": "image_url",
            "image_url": {"url": "data:image/jpeg;base64,/9j/4AAQ..."}
        }
    ]
}
```

## 🔒 Authentication

The framework supports two authentication methods that can be used simultaneously:

### 1. Basic Authentication (Username/Password)

HTTP Basic Authentication using username and password credentials.

**Configuration:**

```env
# Enable authentication
REQUIRE_AUTH=true

# Basic Auth credentials
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=your-secure-password
```

**Usage Examples:**

```bash
# cURL with Basic Auth
curl -u admin:password http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello!"}'

# Python requests
import requests
response = requests.post(
    "http://localhost:8000/message",
    json={"query": "Hello!"},
    auth=("admin", "password")
)
```

### 2. API Key Authentication

More secure option for API clients using bearer tokens or X-API-Key headers.

**Configuration:**

```env
# Enable authentication
REQUIRE_AUTH=true

# API Keys (comma-separated list of valid keys)
API_KEYS=sk-your-secure-key-123,ak-another-api-key-456,my-client-api-key-789
```

**Usage Examples:**

```bash
# cURL with Bearer Token
curl -H "Authorization: Bearer sk-your-secure-key-123" \
  http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello!"}'

# cURL with X-API-Key Header
curl -H "X-API-Key: sk-your-secure-key-123" \
  http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello!"}'

# Python requests with Bearer Token
import requests
headers = {
    "Authorization": "Bearer sk-your-secure-key-123",
    "Content-Type": "application/json"
}
response = requests.post(
    "http://localhost:8000/message",
    json={"query": "Hello!"},
    headers=headers
)

# Python requests with X-API-Key
headers = {
    "X-API-Key": "sk-your-secure-key-123",
    "Content-Type": "application/json"
}
response = requests.post(
    "http://localhost:8000/message",
    json={"query": "Hello!"},
    headers=headers
)
```

### Authentication Priority

The framework tries authentication methods in this order:

1. **API Key via Bearer Token** (`Authorization: Bearer <key>`)
2. **API Key via X-API-Key Header** (`X-API-Key: <key>`)
3. **Basic Authentication** (username/password)

### Python Client Library Support

```python
from AgentClient import AgentClient

# Using Basic Auth
client = AgentClient("http://localhost:8000")
client.session.auth = ("admin", "password")

# Using API Key
client = AgentClient("http://localhost:8000")
client.session.headers.update({"X-API-Key": "sk-your-secure-key-123"})

# Send authenticated request
response = client.send_message("Hello, authenticated world!")
```

### Web Interface Authentication

The web interface (`/testapp`) supports both authentication methods. Update the JavaScript client:

```javascript
// Basic Auth
this.auth = btoa('admin:password');
headers['Authorization'] = `Basic ${this.auth}`;

// API Key
headers['X-API-Key'] = 'sk-your-secure-key-123';
```

### Security Best Practices

1. **Use Strong API Keys**: Generate cryptographically secure random keys
2. **Rotate Keys Regularly**: Update API keys periodically
3. **Environment Variables**: Never hardcode credentials in source code
4. **HTTPS Only**: Always use HTTPS in production to protect credentials
5. **Minimize Key Scope**: Use different keys for different applications/users

**Generate Secure API Keys:**

```bash
# Generate a secure API key (32 bytes, base64 encoded)
python -c "import secrets, base64; print('sk-' + base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('='))"

# Or use openssl
openssl rand -base64 32 | sed 's/^/sk-/'
```

### Disable Authentication

To disable authentication completely:

```env
REQUIRE_AUTH=false
```

When disabled, all endpoints are publicly accessible without any authentication.

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

[Your License Here]

## 🤝 Support

- **Documentation**: This README and inline code comments
- **Examples**: See `test_*.py` files for usage examples
- **Issues**: Report bugs and feature requests via GitHub Issues

---

**Quick Links:**

- [Web Interface](http://localhost:8000/testapp) - Interactive testing
- [API Documentation](http://localhost:8000/docs) - OpenAPI/Swagger docs
- [Configuration Test](http://localhost:8000/config/models) - Validate setup
