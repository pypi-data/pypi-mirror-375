from itertools import product
from pydantic import BaseModel, Field
from openai import OpenAI
import pytest

import instructor
from .util import models, modes


class Item(BaseModel):
    name: str
    price: float


class Order(BaseModel):
    items: list[Item] = Field(default_factory=list)
    customer: str


@pytest.mark.parametrize("model, mode", product(models, modes))
def test_nested(model: str, mode: instructor.Mode, client: OpenAI):
    instructor_client = instructor.from_perplexity(client, mode=mode)
    content = """
    Order Details:
    Customer: Jason
    Items:

    Name: Apple, Price: 0.50
    Name: Bread, Price: 2.00
    Name: Milk, Price: 1.50
    """

    resp = instructor_client.chat.completions.create(
        model=model,
        response_model=Order,
        messages=[
            {
                "role": "user",
                "content": content,
            },
        ],
    )

    assert len(resp.items) == 3
    assert {x.name.lower() for x in resp.items} == {"apple", "bread", "milk"}
    assert {x.price for x in resp.items} == {0.5, 2.0, 1.5}
    assert resp.customer.lower() == "jason"


class Book(BaseModel):
    title: str
    author: str
    genre: str
    isbn: str


class LibraryRecord(BaseModel):
    books: list[Book] = Field(default_factory=list)
    visitor: str
    library_id: str


@pytest.mark.skip()
@pytest.mark.parametrize("model, mode", product(models, modes))
def test_complex_nested_model(model: str, mode: instructor.Mode, client: OpenAI):
    instructor_client = instructor.from_perplexity(client, mode=mode)

    content = """
    Library visit details:
    Visitor: Jason
    Library ID: LIB123456
    Books checked out:
    - Title: The Great Adventure, Author: Jane Doe, Genre: Fantasy, ISBN: 1234567890
    - Title: History of Tomorrow, Author: John Smith, Genre: Non-Fiction, ISBN: 0987654321
    """

    resp = instructor_client.chat.completions.create(
        model=model,
        response_model=LibraryRecord,
        messages=[
            {
                "role": "user",
                "content": content,
            },
        ],
    )

    assert resp.visitor.lower() == "jason"
    assert resp.library_id == "LIB123456"
    assert len(resp.books) == 2
    assert {book.title for book in resp.books} == {
        "The Great Adventure",
        "History of Tomorrow",
    }
    assert {book.author for book in resp.books} == {"Jane Doe", "John Smith"}
    assert {book.genre for book in resp.books} == {"Fantasy", "Non-Fiction"}
    assert {book.isbn for book in resp.books} == {"1234567890", "0987654321"}
