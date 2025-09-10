---
title: Incorporating Examples in Pydantic Models
description: Learn how to enhance Pydantic models with practical examples for clarity and usability in JSON schemas.
---

# How should I include examples?

To enhance the clarity and usability of your model and prompt, incorporating examples directly into the JSON schema extra of your Pydantic model is highly recommended. This approach not only streamlines the integration of practical examples but also ensures that they are easily accessible and understandable within the context of your model's schema.

```python
import openai
import instructor
from typing import Iterable
from pydantic import BaseModel, ConfigDict

client = instructor.from_openai(openai.OpenAI())


class SyntheticQA(BaseModel):
    question: str
    answer: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"question": "What is the capital of France?", "answer": "Paris"},
                {
                    "question": "What is the largest planet in our solar system?",
                    "answer": "Jupiter",
                },
                {
                    "question": "Who wrote 'To Kill a Mockingbird'?",
                    "answer": "Harper Lee",
                },
                {
                    "question": "What element does 'O' represent on the periodic table?",
                    "answer": "Oxygen",
                },
            ]
        }
    )


def get_synthetic_data() -> Iterable[SyntheticQA]:
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Generate synthetic examples"},
            {
                "role": "user",
                "content": "Generate the exact examples you see in the examples of this prompt. ",
            },
        ],
        response_model=Iterable[SyntheticQA],
    )  # type: ignore


if __name__ == "__main__":
    for example in get_synthetic_data():
        print(example)
        #> question='What is the capital of France?' answer='Paris'
        #> question='What is the largest planet in our solar system?' answer='Jupiter'
        #> question="Who wrote 'To Kill a Mockingbird'?" answer='Harper Lee'
        """
        question="What element does 'O' represent on the periodic table?" answer='Oxygen'
        """
        """
        question="What element does 'O' represent on the periodic table?" answer='Oxygen'
        """
```