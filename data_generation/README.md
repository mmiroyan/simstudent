# Data Generation

`templates.py`: Prompt templates for generating using fine-tuned and prompt-based models for experiments 1 and 2.

`utils.py`: Utility functions for data processing used in `generate.py`.

`generate.py`: Generation script, supporting 1) locally running models (`AutoModelForCausalLM` with `generate` method), 2) locally running vLLM chat (OpenAI-compatible) endpoint, 3) API-based models through Azure's OpenAI API. Generation configs for models and experiments are in `configs/`. Input data format is the same as the training data (described in `../fine_tuning`).
