---
title: "Google Gemini Tutorial: Structured Outputs with Instructor"
description: "Learn how to use Google's Gemini models (Pro, Flash, Ultra) with Instructor for structured data extraction. Complete tutorial with examples for multimodal AI and type-safe outputs."
---

# Google Gemini Tutorial: Structured Outputs with Instructor

Master structured data extraction using Google's Gemini models with Instructor. This comprehensive tutorial covers Gemini Pro, Flash, and Ultra models, including multimodal capabilities for processing text, images, and more.

## Google GenAI SDK

Google's GenAI SDK is the recommended way to access Gemini models. It provides a unified interface for both the Gemini API and Vertex AI. This guide shows you how to use Instructor with Google's GenAI SDK for type-safe, validated responses.

```bash
pip install "instructor[google-genai]"
```

## Simple User Example (Sync)

```python
import instructor
from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int


# Using from_provider (recommended)
client = instructor.from_provider(
    "google/gemini-1.5-flash-latest",
)

# note that client.chat.completions.create will also work
resp = client.messages.create(
    messages=[
        {
            "role": "user",
            "content": "Extract Jason is 25 years old.",
        }
    ],
    response_model=User,
)

print(resp)  # User(name='Jason', age=25)
```

## Simple User Example (Async)

!!! info "Async Support"

    Instructor supports async mode for the Google GenAI SDK. If you're using the async client, make sure that your client is declared within the same event loop as the function that calls it. If not you'll get a bunch of errors.

```python
import instructor
from pydantic import BaseModel
import asyncio


class User(BaseModel):
    name: str
    age: int


async def extract_user():
    client = instructor.from_provider(
        "google/gemini-1.5-flash-latest",
        async_client=True,
    )

    user = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Extract Jason is 25 years old.",
            }
        ],
        response_model=User,
    )
    return user


# Run async function
user = asyncio.run(extract_user())
print(user)  # User(name='Jason', age=25)
```

## Configuration Options

You can customize the model's behavior using generation configuration parameters. These parameters control aspects like temperature, token limits, and sampling methods. Pass these parameters as a dictionary to the `generation_config` parameter when creating the response.

The most common parameters include:
- `temperature`: Controls randomness in the output (0.0 to 1.0)
- `max_tokens`: Maximum number of tokens to generate
- `top_p`: Nucleus sampling parameter
- `top_k`: Number of highest probability tokens to consider

For more details on configuration options, see [Google's documentation on Gemini configuration parameters](https://cloud.google.com/vertex-ai/generative-ai/docs/samples/generativeaionvertexai-gemini-pro-config-example){target="_blank"}.


```python
import instructor
import google.generativeai as genai
from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int


client = instructor.from_provider(
    "google/gemini-1.5-flash-latest",
    mode=instructor.Mode.GEMINI_JSON,
)

# note that client.chat.completions.create will also work
resp = client.messages.create(
    messages=[
        {
            "role": "user",
            "content": "Extract Jason is 25 years old.",
        },
    ],
    response_model=User,
    generation_config={
        "temperature": 0.5,
        "max_tokens": 1000,
        "top_p": 1,
        "top_k": 32,
    },
)

print(resp)
```

## Nested Example

```python
import instructor
import google.generativeai as genai
from pydantic import BaseModel


class Address(BaseModel):
    street: str
    city: str
    country: str


class User(BaseModel):
    name: str
    age: int
    addresses: list[Address]


client = instructor.from_provider(
    "google/gemini-1.5-flash-latest",
)

user = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": """
            Extract: Jason is 25 years old.
            He lives at 123 Main St, New York, USA
            and has a summer house at 456 Beach Rd, Miami, USA
        """,
        },
    ],
    response_model=User,
)

print(user)
#> {
#>     'name': 'Jason',
#>     'age': 25,
#>     'addresses': [
#>         {
#>             'street': '123 Main St',
#>             'city': 'New York',
#>             'country': 'USA'
#>         },
#>         {
#>             'street': '456 Beach Rd',
#>             'city': 'Miami',
#>             'country': 'USA'
#>         }
#>     ]
#> }
```

## Streaming Support

Instructor has two main ways that you can use to stream responses out

1. **Iterables**: These are useful when you'd like to stream a list of objects of the same type (Eg. use structured outputs to extract multiple users)
2. **Partial Streaming**: This is useful when you'd like to stream a single object and you'd like to immediately start processing the response as it comes in.

### Partials

```python
import instructor
import google.generativeai as genai
from pydantic import BaseModel


client = instructor.from_provider(
    "google/gemini-1.5-flash-latest",
)


class User(BaseModel):
    name: str
    age: int
    bio: str


user = client.chat.completions.create_partial(
    messages=[
        {
            "role": "user",
            "content": "Create a user profile for Jason and 1 sentence bio, age 25",
        },
    ],
    response_model=User,
)

for user_partial in user:
    print(user_partial)
    # > name=None age=None bio=None
    # > name=None age=25 bio='Jason is a great guy'
    # > name='Jason' age=25 bio='Jason is a great guy'
```

### Iterable Example

```python
import instructor
from pydantic import BaseModel


client = instructor.from_provider(
    "google/gemini-1.5-flash-latest",
)


class User(BaseModel):
    name: str
    age: int


# Extract multiple users from text
users = client.chat.completions.create_iterable(
    messages=[
        {
            "role": "user",
            "content": """
            Extract users:
            1. Jason is 25 years old
            2. Sarah is 30 years old
            3. Mike is 28 years old
        """,
        },
    ],
    response_model=User,
)

for user in users:
    print(user)
    #> name='Jason' age=25
    #> name='Sarah' age=30
    #> name='Mike' age=28
```

## Instructor Modes

We provide several modes to make it easy to work with the different response models that Gemini supports:

1. `instructor.Mode.GENAI_TOOLS` : This uses Gemini's tool calling API to return structured outputs (default)
2. `instructor.Mode.GENAI_STRUCTURED_OUTPUTS` : This uses Gemini's JSON schema mode for structured outputs

!!! info "Mode Selection"
    When using `from_provider`, the appropriate mode is automatically selected based on the provider and model capabilities.

## Available Models

Google offers several Gemini models:

- Gemini Flash (General purpose)
- Gemini Pro (Multimodal)
- Gemini Flash-8b (Coming soon)

## Using Gemini's Multimodal Capabilities

We've written an extensive list of guides on how to use gemini's multimodal capabilities with instructor.

- [Using Geminin To Extract Travel Video Recomendations](../blog/posts/multimodal-gemini.md)
- [Parsing PDFs with Gemini](../blog/posts/chat-with-your-pdf-with-gemini.md)
- [Generating Citations with Gemini](../blog/posts/generating-pdf-citations.md)

Stay tuned to the blog for more guides on using Gemini with instructor.

## Related Resources

- [Google AI Documentation](https://ai.google.dev/)
- [Instructor Core Concepts](../concepts/index.md)
- [Type Validation Guide](../concepts/validation.md)
- [Advanced Usage Examples](../examples/index.md)

## Migration from google-generativeai

If you're currently using the legacy `google-generativeai` package with Instructor, here's how to migrate:

### Old Way (Deprecated)
```python
import instructor
import google.generativeai as genai

client = instructor.from_gemini(
    genai.GenerativeModel("gemini-1.5-flash"),
    mode=instructor.Mode.GEMINI_JSON,
)
```

### New Way (Recommended)
```python
import instructor

# Option 1: Using from_provider (simplest)
client = instructor.from_provider("google/gemini-1.5-flash")

# Option 2: Using from_genai directly
from google import genai
from instructor import from_genai

client = from_genai(genai.Client())
```

### Vertex AI Migration

For Vertex AI users, the migration is similar:

#### Old Way (Deprecated)
```python
import instructor
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="your-project", location="us-central1")
client = instructor.from_vertexai(
    GenerativeModel("gemini-1.5-flash"),
    mode=instructor.Mode.VERTEXAI_TOOLS,
)
```

#### New Way (Recommended)
```python
import instructor

# Option 1: Using from_provider
client = instructor.from_provider(
    "vertexai/gemini-1.5-flash",
    project="your-project",
    location="us-central1"
)

# Option 2: Using from_genai with vertexai=True
from google import genai
from instructor import from_genai

client = from_genai(
    genai.Client(
        vertexai=True,
        project="your-project",
        location="us-central1"
    )
)
```

## Updates and Compatibility

Instructor maintains compatibility with Google's latest API versions. Check the [changelog](https://github.com/jxnl/instructor/blob/main/CHANGELOG.md) for updates.
