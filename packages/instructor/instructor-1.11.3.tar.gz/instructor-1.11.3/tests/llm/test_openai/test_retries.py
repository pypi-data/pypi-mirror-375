from typing import Annotated
from pydantic import AfterValidator, BaseModel, Field
import pytest
import instructor
from itertools import product

models = ["gpt-4.1-mini"]
modes = [
    instructor.Mode.TOOLS,
]


def uppercase_validator(v: str):
    if not v.isupper():
        raise ValueError(
            "All letters in the name should be in uppercase (e.g., TOM, JONES) instead of tom, jones"
        )
    return v.strip()


class UserDetail(BaseModel):
    name: Annotated[str, AfterValidator(uppercase_validator)] = Field(
        ..., description="The name of the user"
    )
    age: int


@pytest.mark.parametrize("model, mode", product(models, modes))
@pytest.mark.asyncio()
async def test_upper_case_async(model, mode, aclient):
    client = instructor.from_openai(aclient, mode=mode)
    response = await client.chat.completions.create(
        model=model,
        response_model=UserDetail,
        messages=[
            {"role": "user", "content": "Extract `jason is 12`"},
        ],
        max_retries=3,
    )
    assert response.name == "JASON"


@pytest.mark.parametrize("model, mode", product(models, modes))
@pytest.mark.asyncio()
async def test_upper_case_tenacity_async(model, mode, aclient):
    client = instructor.from_openai(aclient, mode=mode)
    from tenacity import AsyncRetrying, stop_after_attempt, wait_fixed

    retries = AsyncRetrying(
        stop=stop_after_attempt(2),
        wait=wait_fixed(1),
    )

    response = await client.chat.completions.create(
        model=model,
        response_model=UserDetail,
        messages=[
            {"role": "user", "content": "Extract `jason is 12`"},
        ],
        max_retries=retries,
    )
    assert response.name == "JASON"


@pytest.mark.parametrize("model, mode", product(models, modes))
def test_upper_case(model, mode, client):
    client = instructor.from_openai(client, mode=mode)
    response = client.chat.completions.create(
        model=model,
        response_model=UserDetail,
        messages=[
            {"role": "user", "content": "Extract `jason is 12`"},
        ],
        max_retries=3,
    )
    assert response.name == "JASON"


@pytest.mark.parametrize("model, mode", product(models, modes))
def test_upper_case_tenacity(model, mode, client):
    client = instructor.from_openai(client, mode=mode)
    from tenacity import Retrying, stop_after_attempt, wait_fixed

    retries = Retrying(
        stop=stop_after_attempt(2),
        wait=wait_fixed(1),
    )

    response = client.chat.completions.create(
        model=model,
        response_model=UserDetail,
        messages=[
            {"role": "user", "content": "Extract `jason is 12`"},
        ],
        max_retries=retries,
    )
    assert response.name == "JASON"


@pytest.mark.parametrize("model, mode", product(models, modes))
def test_custom_retry_response_error(model, mode):
    from openai import OpenAI

    client = OpenAI()

    client.api_key = "incorrect_key"

    client = instructor.from_openai(client, mode=mode)
    from openai import AuthenticationError
    from instructor.core.exceptions import InstructorRetryException
    from tenacity import Retrying, retry_if_not_exception_type, stop_after_attempt

    retries = Retrying(
        retry=retry_if_not_exception_type(ZeroDivisionError), stop=stop_after_attempt(1)
    )
    try:
        client.chat.completions.create(
            model=model,
            max_retries=retries,
            messages=[
                {
                    "role": "user",
                    "content": "Jason is 25 years old",
                }
            ],
            response_model=UserDetail,
        )
    except InstructorRetryException as e:
        root_cause = e
        while root_cause.__cause__ is not None:
            root_cause = root_cause.__cause__

        assert isinstance(root_cause, AuthenticationError)
        assert e.last_completion is None
