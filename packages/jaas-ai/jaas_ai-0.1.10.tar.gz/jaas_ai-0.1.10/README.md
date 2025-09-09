# JaaS API Python SDK

[![PyPI version](https://badge.fury.io/py/jaas_ai.svg)](https://badge.fury.io/py/jaas_ai)
[![Python Support](https://img.shields.io/pypi/pyversions/jaas_ai.svg)](https://pypi.org/project/jaas_ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python SDK for interacting with the JaaS AI evaluation API. This library provides a simple and intuitive interface for evaluating AI-generated responses against various criteria.

Visit jaas-ai.net for more information.
Note: a JaaS AI API key is required. 

## Features

- 🚀 Simple and intuitive API
- 🔧 Support for multiple evaluation types (S, C, D, V), with multiple citeria
- 📊 Comprehensive evaluation criteria support including Hallucination Detection
- 🛡️ Robust error handling
- 📝 Type hints for better IDE support
- 🐍 Python 3.7+ support

## Installation

### From PyPI (recommended)

```bash
pip install jaas_ai
```


## Quick Start

```python
from jaas_ai import jaas_client

# Initialize the client with your API key
client = jaas_client(api_key="your-api-key-here")

# Evaluate an AI response
result = client.evaluate(
    question="What is the capital of France?",
    answer="The capital of France is Paris.",
    evaluation_criteria=["accuracy", "completeness", "clarity"],
    eval_type="S"
)

# Check if the request was successful
if result["status"] == "success":
    print("Evaluation results:", result["data"])
else:
    print("Error:", result["error"])
```

## API Reference

### jaas_client

The main client class for interacting with the JaaS API.

#### Constructor

```python
jaas_client(api_key: str)
```

- `api_key` (str): Your JaaS API key

#### Methods

##### evaluate()

Submit an evaluation request to the JaaS API.

```python
def evaluate(
    self,
    question: str,
    answer: str,
    evaluation_criteria: List[str],
    eval_type: str = "S",
    ground_truth_answer: Optional[str] = None,
    context: Optional[str] = None,
    cohort: Optional[str] = None
) -> Dict
```

**Parameters:**

- `question` (str): The input question
- `answer` (str): The AI-generated answer to evaluate
- `evaluation_criteria` (List[str]): List of criteria to evaluate against
- `eval_type` (str, optional): Evaluation type. Options:
- `ground_truth_answer` (str, optional): Reference answer for comparison
- `context` (str, optional): Additional context for evaluation
- `cohort` (str, optional): Cohort name for grouping evaluations

**Returns:**

- `Dict`: Response with consistent structure:
  - **Success**: `{"status": "success", "data": {...}}`
  - **Error**: `{"status": "error", "error": "error message"}`

**Error Handling:**

The method returns structured responses instead of raising exceptions:
- Check `result["status"]` to determine success or failure
- On success: access data via `result["data"]`
- On error: get error message via `result["error"]`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: info@jaas-ai.com
- 📖 Documentation: [https://jaas-ai.net ]

## Response Format

All API responses follow a consistent structure:

### Success Response
```json
{
    "status": "success",
    "data": {
        // Evaluation results from JaaS API
    }
}
```

### Error Response
```json
{
    "status": "error",
    "error": "Error message describing what went wrong"
}
```

## Changelog

### v0.1.10 (2025-09-08)
- Implemented structured response format
- All responses now include `status` and `data`/`error` fields
- Improved error handling with consistent JSON structure
- No more exceptions - all errors returned as structured responses

### v0.1.5 (2025-09-08)
- Improved error handling with cleaner error messages
- Better HTTP error reporting from server responses

### v0.1.4 (2025-09-08)
- Simplified use and API call
- Improved evaluation functionality
- Support for multiple evaluation types
- Comprehensive error handling

