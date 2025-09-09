"""Together AI API Helper Package.

A Python package that provides high-level utilities for working with Together AI's API,
including endpoint management and fine-tuning capabilities.

This package includes:
- Common utilities and base client functionality
- Endpoint management for dedicated model deployments
- Fine-tuning job management and monitoring

Example:
    from together_ai_api_helper.endpoints import EndpointClient, EndpointConfig
    from together_ai_api_helper.training import TrainingClient, TrainingConfig

    # Manage endpoints
    endpoint_client = EndpointClient()
    config = EndpointConfig(model_name="mistralai/Mistral-7B-Instruct-v0.1")
    endpoint_name, endpoint_id = endpoint_client.get_endpoint_for_model(config)

    # Fine-tune models
    training_client = TrainingClient()
    train_config = TrainingConfig(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        training_file="data.jsonl",
        suffix="my-model"
    )
    model_name = training_client.start_job(train_config)
"""
