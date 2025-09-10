# Pangea + Azure AI Inference SDK

A wrapper around the Azure AI Inference SDK that wraps the chat completion API
with Pangea AI Guard. Supports Python v3.10 and greater.

## Installation

```bash
pip install -U pangea-azure-ai
```

## Usage

```python
import os

from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

from pangea_azure_ai.inference import PangeaChatCompletionsClient

endpoint = "https://[...].cognitiveservices.azure.com/openai/deployments/gpt-4o-mini"
model_name = "gpt-4o-mini"

client = PangeaChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(os.getenv("AZURE_API_KEY", "")),
    pangea_api_key=os.getenv("PANGEA_API_KEY", ""),
)

response = client.complete(
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="I am going to Paris, what should I see?"),
    ],
    max_tokens=4096,
    temperature=1.0,
    top_p=1.0,
    model=model_name,
    stream=False,
)

print(response.choices[0].message.content)
```
