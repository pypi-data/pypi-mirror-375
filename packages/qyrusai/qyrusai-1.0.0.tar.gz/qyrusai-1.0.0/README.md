# QyrusAI Python SDK

The **QyrusAI Python SDK** provides a _Python client_ to access our **_SOTA Single Use testing Agents_** for _test case generation_, _test data generation_, _API test case generation_, and many more.

## Key Features

- **Nova:** Nova provides a quick and easy way to generate test scenarios and test cases using JIRA tickets, User story documents and Rally Tickets.
- **Nova API Assertions:** Nova API Assertions provide a quick way to create assertions to test API responses. These assertions include _header, schema, JSON Path, and JSON Body_ test cases.
- **API Builder**: API builder helps in visualizing virtualized APIs and provide a well planned Swagger documentation with APIs for the provided use case description.
- **Vision Nova**: Vision Nova helps in creating functional tests from Figma design frames.
- **Data Amplification**: Data Amplification helps create highly realistic context specific data for testing needs.
- **LLM Evaluator**: LLM Evaluator provides comprehensive evaluation for RAG (Retrieval-Augmented Generation) and MCP (Model Context Protocol) systems with advanced metrics.

## Installation

You can install `qyrusai` from the source as of now.

### From Source

```
pip install git+https://github.com/QQyrus/qyrusai-sdk.git
```

## Usage

### Initialize QyrusAI SDK

```py
from qyrusai import AsyncQyrusAI

async def jira_test():
    client = AsyncQyrusAI(api_key="your_api_key")

    result = await client.nova.from_jira.create(
        jira_endpoint="https://your-domain.atlassian.net",
        jira_api_token="your_jira_token",
        jira_username="your_jira_email",
        jira_id="PROJ-123"
    )

    print(f"Generated {len(result.scenarios)} test scenarios")
    for scenario in result.scenarios:
        print(f"- {scenario.test_script_name} (Score: {scenario.criticality_score})")

    return result

if __name__ == "__main__":
    import asyncio
    asyncio.run(jira_test())
```

### Create Tests via User Description

```py
from qyrusai import SyncQyrusAI

client = SyncQyrusAI(api_key="your_api_key")

result = client.nova.from_description.create(
    user_description="Create tests for login page"
)

print(f"Generated {len(result.scenarios)} test scenarios")
for scenario in result.scenarios:
    print(f"- {scenario.test_script_name}")
```

### Create Tests for Rally Ticket

```py
from qyrusai import AsyncQyrusAI

async def rally_test():
    client = AsyncQyrusAI(api_key="your_api_key")

    result = await client.nova.from_rally.create(
        TICKET_ID="US12345",
        WORKSPACE_NAME="Your Workspace",
        RALLY_URL="https://rally1.rallydev.com",
        RALLY_API_KEY="your_rally_api_key"
    )

    return result
```

## Data Amplification

### Generate Realistic Test Data

```py
from qyrusai import SyncQyrusAI

client = SyncQyrusAI(api_key="your_api_key")

# Define your data structure
data = [
    {
        "column_name": "first_name",
        "column_description": "User's first name",
        "column_restriction": "no restrictions",
        "column_values": ["John", "Jane", "Michael", "Emily", "Sarah"]
    },
    {
        "column_name": "email",
        "column_description": "User's email address",
        "column_restriction": "valid email format",
        "column_values": ["john@example.com", "jane@test.com"]
    }
]

# Generate 10 new rows of data
result = client.data_amplifier.amplify(data, data_count=10)

print("Generated data:")
for key, values in result.data.items():
    print(f"{key}: {values}")
```

## API Builder

### Generate API Documentation from Description

```py
from qyrusai import SyncQyrusAI

client = SyncQyrusAI(api_key="your_api_key")

swagger_spec = client.api_builder.build(
    email="developer@company.com",
    user_description="Generate APIs for e-commerce platform with user management and product catalog"
)

print("Generated Swagger specification:")
print(f"Title: {swagger_spec['info']['title']}")
print(f"Paths: {list(swagger_spec['paths'].keys())}")
```

## API Assertions

### Generate Header Assertions

```py
from qyrusai import SyncQyrusAI

client = SyncQyrusAI(api_key="your_api_key")


assertions = client.api_assertions.headers.create(headers=headers)

for assertion in assertions:
    print(f"Assert {assertion['assertHeaderKey']}: {assertion['assertHeaderValue']}")
```

### Generate JSON Body Assertions

```py
response_data = {
    "status": "success",
    "data": {
        "user_id": 123,
        "username": "john_doe",
        "email": "john@example.com"
    },
    "message": "User retrieved successfully"
}

assertions = client.api_assertions.jsonbody.create(response=response_data)

for assertion in assertions:
    print(f"Assert contains: {assertion['value']} - {assertion['assertionDescription']}")
```

### Generate JSON Path Assertions

```py
jsonpath_assertions = client.api_assertions.jsonpath.create(response=response_data)

for assertion in jsonpath_assertions:
    print(f"JSONPath: {assertion['jsonPath']} == {assertion['jsonPathValue']}")
```

### Generate JSON Schema Assertions

```py
schema = client.api_assertions.jsonschema.create(response=response_data)

print("Generated JSON Schema:")
print(schema)
```

## Vision Nova

### Generate Tests from UI Images

```py
from qyrusai import SyncQyrusAI

client = SyncQyrusAI(api_key="your_api_key")

# Generate functional tests from image URL
image_url = "https://example.com/login-page-screenshot.jpg"
test_scenarios = client.vision_nova.generate_test.generate(image_url)

print(f"Generated {len(test_scenarios.scenarios)} test scenarios from image:")
for scenario in test_scenarios.scenarios:
    print(f"- {scenario['scenario_name']}: {scenario['objective']}")
    print(f"  Steps: {len(scenario['steps'])} steps")
```

### Verify UI Accessibility

```py
# Verify accessibility compliance of UI design
accessibility_report = client.vision_nova.verify_accessibility.verify(image_url)

print("Accessibility Report:")
for item in accessibility_report.visual_accessibility:
    print(f"- {item['accessibility_type']}: {item['accessibility_comment']}")
```

## LLM Evaluator

### Initialize LLM Evaluator

```py
from qyrusai import AsyncQyrusAI
from qyrusai._types import RAGRequest, MCPRequest

client = AsyncQyrusAI(api_key="your_api_key")
evaluator = client.llm_evaluator.evaluator
```

### Evaluate RAG (Retrieval-Augmented Generation) Systems

```py
# Basic RAG evaluation
rag_request = RAGRequest(
    app_name="customer_support_rag",
    qid="test_001",
    question="How do I reset my password?",
    answer="Click 'Forgot Password' on the sign-in page. The reset link expires in 24 hours.",
    retrieved=[
        {
            "doc_id": "kb-12",
            "text": "To reset your password, click 'Forgot Password' on the sign-in page. An email link is valid for 24 hours.",
            "score": 0.89
        }
    ],
    citations=[0],
    params={"model": "gpt-4o-mini", "temperature": 0.2}
)

# Evaluate the RAG system
result = await evaluator.evaluate_rag(rag_request)
print(f"Status: {result['status']}")
print(f"Faithfulness: {result['metrics']['faithfulness']}")
print(f"Relevance: {result['metrics']['relevance']}")
```

### Evaluate MCP (Model Context Protocol) Tool-Calling Systems

```py
# Basic MCP evaluation
mcp_request = MCPRequest(
    app_name="customer_support_mcp",
    qid="test_002",
    question="What's my order status?",
    answer="Your order ABC-123 has shipped and will arrive tomorrow.",
    tools=[
        {
            "name": "orders.getStatus",
            "args": {"order_id": "ABC-123"},
            "args_valid": True,
            "status": "ok",
            "latency_ms": 150,
            "result_text": "Order ABC-123 status: shipped, estimated delivery: tomorrow"
        }
    ]
)

# Evaluate the MCP system
result = await evaluator.evaluate_mcp(mcp_request)
print(f"Status: {result['status']}")
print(f"Tool Selection Quality: {result['metrics']['tool_selection_quality']}")
print(f"Args Valid Rate: {result['metrics']['args_valid_rate']}")
```

### Batch Evaluation

```py
# Evaluate multiple requests at once
requests = [rag_request, mcp_request]

batch_result = await evaluator.evaluate_batch(requests)
print(f"Total: {batch_result['total']}")
print(f"Successful: {batch_result['successful']}")
print(f"Failed: {batch_result['failed']}")

for result in batch_result['results']:
    print(f"- {result['qid']}: {result['status']}")
```

### Using JSON Input (Alternative to Pydantic)

```py
# You can also use plain dictionaries instead of Pydantic models
rag_dict = {
    "app_name": "customer_support_rag",
    "qid": "test_003",
    "question": "What are the pricing plans?",
    "answer": "We offer Basic ($10/month) and Premium ($25/month) plans.",
    "retrieved": [
        {
            "doc_id": "pricing-1",
            "text": "Basic plan costs $10/month. Premium plan costs $25/month.",
            "score": 0.95
        }
    ],
    "citations": [0]
}

# The evaluator automatically validates and converts JSON to Pydantic
result = await evaluator.evaluate_rag(rag_dict)
```

### Legacy Judge Evaluation (Backwards Compatibility)

```py
# Original evaluate method still works
score = await evaluator.evaluate(
    context="User wants to reset password",
    expected_output="Provide reset link instructions",
    executed_output=["Click 'Forgot Password' on login page"],
    guardrails="Always mention link expiration time"
)

print(f"Evaluation score: {score}")
```

### Synchronous Usage

```py
from qyrusai import SyncQyrusAI

# All methods are available in synchronous versions
client = SyncQyrusAI(api_key="your_api_key")
evaluator = client.llm_evaluator.evaluator

# Synchronous RAG evaluation
result = evaluator.evaluate_rag(rag_request)

# Synchronous batch evaluation
batch_result = evaluator.evaluate_batch([rag_request, mcp_request])
```

### Advanced MCP with Schema Validation

```py
# MCP with automatic argument validation
mcp_with_schema = MCPRequest(
    app_name="advanced_mcp_app",
    qid="test_004",
    question="Search for customer orders",
    answer="Found 5 orders for customer John Doe.",
    tool_schemas={
        "database.query": {
            "type": "object",
            "properties": {
                "sql": {"type": "string"},
                "timeout": {"type": "number", "minimum": 1}
            },
            "required": ["sql"]
        }
    },
    tools=[
        {
            "name": "database.query",
            "args": {"sql": "SELECT * FROM orders WHERE customer_name='John Doe'"},
            # args_valid will be automatically computed from schema
            "status": "ok",
            "latency_ms": 245,
            "result_text": "Found 5 orders"
        }
    ]
)

result = await evaluator.evaluate_mcp(mcp_with_schema)
```

## Complete Example

```py
import os
import asyncio
from qyrusai import AsyncQyrusAI
from qyrusai._types import RAGRequest, MCPRequest

async def main():
    # Initialize client
    client = AsyncQyrusAI(api_key=os.getenv("QYRUS_API_KEY"))

    # Generate test scenarios from JIRA
    scenarios = await client.nova.from_description.create(
        "Create tests for user registration form"
    )
    print(f"Generated {len(scenarios.scenarios)} test scenarios")

    # Generate test data
    data_schema = [{
        "column_name": "username",
        "column_description": "unique username",
        "column_restriction": "alphanumeric only",
        "column_values": ["user1", "testuser", "admin"]
    }]

    test_data = client.data_amplifier.amplify(data_schema, data_count=5)
    print(f"Generated test data: {test_data.data}")

    # Build API documentation
    api_spec = client.api_builder.build(
        email="dev@company.com",
        user_description="User management API with registration and authentication"
    )
    print(f"Generated API with {len(api_spec['paths'])} endpoints")

    # Evaluate RAG system
    rag_evaluation = await client.llm_evaluator.evaluator.evaluate_rag({
        "app_name": "help_desk_rag",
        "qid": "eval_001",
        "question": "How to reset password?",
        "answer": "Use the forgot password link",
        "retrieved": [{"doc_id": "kb1", "text": "Click forgot password link", "score": 0.9}],
        "citations": [0]
    })
    print(f"RAG Status: {rag_evaluation['status']}")

if __name__ == "__main__":
    asyncio.run(main())
```

> **Note**: Both Asynchronous and Synchronous interactions are available. Replace `AsyncQyrusAI` with `SyncQyrusAI` and remove `await` for synchronous usage.

> **Note**: Store your API key securely using environment variables. Get your API key from the Qyrus platform.
