# Together AI API Helper

A Python package that provides high-level utilities for working with Together AI's API, making endpoint management and fine-tuning operations simpler and more robust.

## Features

🚀 **Endpoint Management**
- Automatic endpoint provisioning and configuration
- State monitoring and health checks
- Hardware configuration management

🎯 **Fine-Tuning Operations**
- Automated fine-tuning job lifecycle management
- Real-time job monitoring with event streaming
- Training file validation and upload
- Automatic Hugging Face repository creation

## Installation

Install the package from PyPI:

```bash
uv add together-ai-api-helper
```

## Requirements

- Python ≥ 3.13
- Together AI API key
- Hugging Face token (if you want to upload the fine-tuned models)

## Setup

### 1. API tokens

Set your API keys as environment variables. (Note that the HF_TOKEN is optional and is only needed if you want to automatically upload the trained model to HF):

```bash
export TOGETHER_API_KEY="your-api-key-here"
export HF_TOKEN="your-hf-token-here"
```

## Usage

### Endpoint Management

```python
from together_ai_api_helper.endpoints import EndpointClient, EndpointConfig, GenerateConfig

# Initialize the client
client = EndpointClient()

# Configure your endpoint
config = EndpointConfig(
    model_name="mistralai/Mistral-7B-Instruct-v0.1",
    display_name="My Mistral Endpoint",
    # Uses cheapest compatible hardware by default
)

# Get or create an endpoint
endpoint_name, endpoint_id = client.get_endpoint_for_model(config)
print(f"Endpoint ready: {endpoint_name} ({endpoint_id})")
```

### Fine-Tuning

```python
from together_ai_api_helper.training import TrainingClient, TrainingConfig

# Initialize the training client
client = TrainingClient()

# Configure your training job
config = TrainingConfig(
    model="mistralai/Mistral-7B-Instruct-v0.1",
    training_file="path/to/your/training_data.jsonl",
    suffix="my-custom-model",
    n_epochs=3,
    learning_rate=1e-5,
    **other_together_ai_params
)

# Train the model (this will monitor progress automatically)
model_name = client.start_job(config)
```

## Logging

All operations are logged with detailed information. Logs include:

- Endpoint state changes
- Training progress and events
- Error messages and debugging information
- API interactions and timing

Log files are created automatically (can change the file paths):
- `endpoints.log` for endpoint operations
- `training.log` for fine-tuning operations

## API Reference

### EndpointClient Methods

- `get_endpoint_for_model(config)` - Get or create an endpoint
- `list_active_endpoints()` - List all active endpoints
- `list_inactive_endpoints()` - List all inactive endpoints
- `restart_endpoint(endpoint_id)` - Restart a stopped endpoint
- `stop_endpoint(endpoint_id)` - Stop a running endpoint
- `delete_endpoint(endpoint_id)` - Delete an endpoint

### TrainingClient Methods

- `start_job(config)` - Start and monitor a fine-tuning job
- `monitor_job(job_id)` - Monitor an existing job
- `cancel_job(job_id)` - Cancel a running job

## Contributing

This package builds on top of the official [Together Python SDK](https://github.com/togethercomputer/together-python).

For development use the dev extra dependencies:

```bash
uv sync --extra dev
```

Note that the linting and type checking will run automatically in pre-commit.

### License

MIT License

### Support

For issues and questions:
- Check the [Together AI documentation](https://docs.together.ai/)
- Review the official [Together Python SDK](https://github.com/togethercomputer/together-python)
- Open an issue in this repository