# cheeky-platform-shared

Shared utilities for the Cheeky Platform - AI-powered Shopify analytics.

## Installation

```bash
pip install cheeky-platform-shared
```

## Usage

```python
from cheeky_platform_shared.llm import openai_chat_text
from cheeky_platform_shared.prompts import (
    BASE_CONTEXT_SYSTEM_PROMPT,
    BASE_CONTEXT_USER_PROMPT,
)

text = await openai_chat_text(
    system=BASE_CONTEXT_SYSTEM_PROMPT,
    user=BASE_CONTEXT_USER_PROMPT.format(url="https://shop.example", content="...")
)
```

## License

MIT