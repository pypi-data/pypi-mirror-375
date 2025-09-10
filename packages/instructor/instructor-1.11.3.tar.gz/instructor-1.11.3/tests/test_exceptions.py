"""Test that all instructor exceptions can be imported and caught properly."""

import pytest
from json import JSONDecodeError
from instructor.core.exceptions import (
    InstructorError,
    IncompleteOutputException,
    InstructorRetryException,
    ValidationError,
    ProviderError,
    ConfigurationError,
    ModeError,
    ClientError,
    FailedAttempt,
)


def test_all_exceptions_can_be_imported():
    """Test that all exceptions can be imported from instructor base package"""
    # This test passes if the imports above succeed
    assert InstructorError is not None
    assert IncompleteOutputException is not None
    assert InstructorRetryException is not None
    assert ValidationError is not None
    assert ProviderError is not None
    assert ConfigurationError is not None
    assert ModeError is not None
    assert ClientError is not None


def test_exception_hierarchy():
    """Test that all exceptions inherit from InstructorError."""
    assert issubclass(IncompleteOutputException, InstructorError)
    assert issubclass(InstructorRetryException, InstructorError)
    assert issubclass(ValidationError, InstructorError)
    assert issubclass(ProviderError, InstructorError)
    assert issubclass(ConfigurationError, InstructorError)
    assert issubclass(ModeError, InstructorError)
    assert issubclass(ClientError, InstructorError)


def test_base_instructor_error_can_be_caught():
    """Test that InstructorError can catch all instructor exceptions."""
    with pytest.raises(InstructorError):
        raise IncompleteOutputException()

    with pytest.raises(InstructorError):
        raise InstructorRetryException(n_attempts=3, total_usage=100)

    with pytest.raises(InstructorError):
        raise ValidationError("Validation failed")

    with pytest.raises(InstructorError):
        raise ProviderError("openai", "API error")

    with pytest.raises(InstructorError):
        raise ConfigurationError("Invalid config")

    with pytest.raises(InstructorError):
        raise ModeError("tools", "openai", ["json"])

    with pytest.raises(InstructorError):
        raise ClientError("Client initialization failed")


def test_incomplete_output_exception():
    """Test IncompleteOutputException attributes and catching."""
    last_completion = {"content": "partial response"}

    with pytest.raises(IncompleteOutputException) as exc_info:
        raise IncompleteOutputException(last_completion=last_completion)

    assert exc_info.value.last_completion == last_completion
    assert "incomplete due to a max_tokens length limit" in str(exc_info.value)


def test_instructor_retry_exception():
    """Test InstructorRetryException attributes and catching."""
    last_completion = {"content": "failed response"}
    messages = [{"role": "user", "content": "test"}]
    n_attempts = 3
    total_usage = 150
    create_kwargs = {"model": "gpt-3.5-turbo"}

    with pytest.raises(InstructorRetryException) as exc_info:
        raise InstructorRetryException(
            last_completion=last_completion,
            messages=messages,
            n_attempts=n_attempts,
            total_usage=total_usage,
            create_kwargs=create_kwargs,
        )

    exception = exc_info.value
    assert exception.last_completion == last_completion
    assert exception.messages == messages
    assert exception.n_attempts == n_attempts
    assert exception.total_usage == total_usage
    assert exception.create_kwargs == create_kwargs


def test_validation_error():
    """Test ValidationError can be caught."""
    error_message = "Field validation failed"

    with pytest.raises(ValidationError) as exc_info:
        raise ValidationError(error_message)

    assert str(exc_info.value) == error_message


def test_provider_error():
    """Test ProviderError attributes and catching."""
    provider = "anthropic"
    message = "Rate limit exceeded"

    with pytest.raises(ProviderError) as exc_info:
        raise ProviderError(provider, message)

    exception = exc_info.value
    assert exception.provider == provider
    assert f"{provider}: {message}" in str(exception)


def test_configuration_error():
    """Test ConfigurationError can be caught."""
    error_message = "Missing required configuration"

    with pytest.raises(ConfigurationError) as exc_info:
        raise ConfigurationError(error_message)

    assert str(exc_info.value) == error_message


def test_mode_error():
    """Test ModeError attributes and catching."""
    mode = "invalid_mode"
    provider = "openai"
    valid_modes = ["json", "tools", "functions"]

    with pytest.raises(ModeError) as exc_info:
        raise ModeError(mode, provider, valid_modes)

    exception = exc_info.value
    assert exception.mode == mode
    assert exception.provider == provider
    assert exception.valid_modes == valid_modes
    assert f"Invalid mode '{mode}' for provider '{provider}'" in str(exception)
    assert "json, tools, functions" in str(exception)


def test_client_error():
    """Test ClientError can be caught."""
    error_message = "Client not properly initialized"

    with pytest.raises(ClientError) as exc_info:
        raise ClientError(error_message)

    assert str(exc_info.value) == error_message


def test_specific_exception_catching():
    """Test that specific exceptions can be caught individually."""
    # Test that we can catch specific exceptions without catching others

    with pytest.raises(IncompleteOutputException):
        try:
            raise IncompleteOutputException()
        except InstructorRetryException:
            pytest.fail("Should not catch InstructorRetryException")
        except IncompleteOutputException:
            raise  # Re-raise to be caught by pytest.raises

    with pytest.raises(ProviderError):
        try:
            raise ProviderError("test", "error")
        except ConfigurationError:
            pytest.fail("Should not catch ConfigurationError")
        except ProviderError:
            raise  # Re-raise to be caught by pytest.raises


def test_multiple_exception_handling():
    """Test handling multiple exception types in a single try-except block."""

    def raise_exception(exc_type: str):
        if exc_type == "incomplete":
            raise IncompleteOutputException()
        elif exc_type == "retry":
            raise InstructorRetryException(n_attempts=3, total_usage=100)
        elif exc_type == "validation":
            raise ValidationError("validation failed")
        else:
            raise ValueError("unknown exception type")

    # Test catching multiple specific exceptions
    for exc_type in ["incomplete", "retry", "validation"]:
        with pytest.raises(
            (IncompleteOutputException, InstructorRetryException, ValidationError)
        ):
            raise_exception(exc_type)

    # Test that base exception catches all instructor exceptions
    for exc_type in ["incomplete", "retry", "validation"]:
        with pytest.raises(InstructorError):
            raise_exception(exc_type)

    # Test that non-instructor exceptions are not caught
    with pytest.raises(ValueError):
        raise_exception("unknown")


def test_exception_import_from_instructor():
    """Test that exceptions can be imported from the main instructor module."""
    # Test importing from instructor.exceptions (already done in module imports)
    from instructor.core.exceptions import InstructorError as ImportedError

    assert ImportedError is InstructorError

    # Test that exceptions are accessible and can be used in real scenarios
    try:
        raise ImportedError("test error")
    except InstructorError as e:
        assert str(e) == "test error"


def test_instructor_error_from_exception():
    """Test InstructorError.from_exception() class method."""
    # Test with basic exception
    original_exception = ValueError("Original error message")
    instructor_error = InstructorError.from_exception(original_exception)

    assert isinstance(instructor_error, InstructorError)
    assert str(instructor_error) == "Original error message"
    assert instructor_error.failed_attempts is None

    # Test with failed attempts
    failed_attempts = [
        FailedAttempt(1, Exception("First failure"), "partial completion"),
        FailedAttempt(2, Exception("Second failure"), None),
    ]
    instructor_error_with_attempts = InstructorError.from_exception(
        original_exception, failed_attempts=failed_attempts
    )

    assert isinstance(instructor_error_with_attempts, InstructorError)
    assert instructor_error_with_attempts.failed_attempts == failed_attempts

    # Test with different exception types
    runtime_error = RuntimeError("Runtime issue")
    instructor_error_runtime = InstructorError.from_exception(runtime_error)
    assert str(instructor_error_runtime) == "Runtime issue"


def test_instructor_error_str_with_no_failed_attempts():
    """Test InstructorError.__str__() with no failed attempts."""
    error = InstructorError("Simple error message")
    assert str(error) == "Simple error message"

    error_with_args = InstructorError("Error", "with", "multiple", "args")
    assert "Error" in str(error_with_args)


def test_instructor_error_str_with_failed_attempts():
    """Test InstructorError.__str__() XML template rendering with failed attempts."""
    # Create failed attempts
    failed_attempts = [
        FailedAttempt(1, ValueError("Validation failed"), "incomplete response"),
        FailedAttempt(2, KeyError("Missing key"), {"partial": "data"}),
        FailedAttempt(3, RuntimeError("Process failed"), None),
    ]

    error = InstructorError("Final error message", failed_attempts=failed_attempts)
    error_str = str(error)

    # Check that XML structure is present
    assert "<failed_attempts>" in error_str
    assert "</failed_attempts>" in error_str
    assert "<last_exception>" in error_str
    assert "</last_exception>" in error_str

    # Check that all attempts are included
    assert 'number="1"' in error_str
    assert 'number="2"' in error_str
    assert 'number="3"' in error_str

    # Check that exceptions are included
    assert "Validation failed" in error_str
    assert "Missing key" in error_str
    assert "Process failed" in error_str

    # Check that completions are included
    assert "incomplete response" in error_str
    assert "partial" in error_str

    # Check that final exception is included
    assert "Final error message" in error_str


def test_instructor_error_str_xml_structure():
    """Test detailed XML structure of __str__() output."""
    failed_attempts = [FailedAttempt(1, Exception("Test error"), "test completion")]

    error = InstructorError("Last error", failed_attempts=failed_attempts)
    error_str = str(error)

    # Check proper XML nesting
    lines = error_str.strip().split("\n")

    # Find key XML elements
    failed_attempts_start = next(
        i for i, line in enumerate(lines) if "<failed_attempts>" in line
    )
    generation_start = next(
        i for i, line in enumerate(lines) if '<generation number="1">' in line
    )
    exception_start = next(i for i, line in enumerate(lines) if "<exception>" in line)
    completion_start = next(i for i, line in enumerate(lines) if "<completion>" in line)

    # Verify proper nesting order
    assert failed_attempts_start < generation_start < exception_start < completion_start


def test_failed_attempt_namedtuple():
    """Test FailedAttempt NamedTuple functionality."""
    # Test with all fields
    attempt = FailedAttempt(1, Exception("Test error"), "completion data")
    assert attempt.attempt_number == 1
    assert str(attempt.exception) == "Test error"
    assert attempt.completion == "completion data"

    # Test with None completion (default)
    attempt_no_completion = FailedAttempt(2, ValueError("Another error"))
    assert attempt_no_completion.attempt_number == 2
    assert isinstance(attempt_no_completion.exception, ValueError)
    assert attempt_no_completion.completion is None

    # Test immutability
    with pytest.raises(AttributeError):
        attempt.attempt_number = 5


def test_instructor_error_failed_attempts_attribute():
    """Test that failed_attempts attribute is properly handled."""
    # Test default None
    error = InstructorError("Test error")
    assert error.failed_attempts is None

    # Test explicit None
    error_explicit = InstructorError("Test error", failed_attempts=None)
    assert error_explicit.failed_attempts is None

    # Test with actual failed attempts
    attempts = [FailedAttempt(1, Exception("Error"), None)]
    error_with_attempts = InstructorError("Test error", failed_attempts=attempts)
    assert error_with_attempts.failed_attempts == attempts


def test_instructor_retry_exception_with_failed_attempts():
    """Test InstructorRetryException inherits failed_attempts functionality."""
    failed_attempts = [
        FailedAttempt(1, Exception("First error"), "first completion"),
        FailedAttempt(2, Exception("Second error"), "second completion"),
    ]

    retry_exception = InstructorRetryException(
        "Retry exhausted",
        n_attempts=3,
        total_usage=100,
        failed_attempts=failed_attempts,
    )

    # Check that it inherits the XML formatting
    error_str = str(retry_exception)
    assert "<failed_attempts>" in error_str
    assert "First error" in error_str
    assert "Second error" in error_str
    assert "first completion" in error_str
    assert "second completion" in error_str


def test_multiple_exception_types_with_failed_attempts():
    """Test that various exception types work with failed attempts."""
    failed_attempts = [FailedAttempt(1, Exception("Test"), None)]

    # Test various exception types can be created with failed attempts
    validation_error = ValidationError(
        "Validation failed", failed_attempts=failed_attempts
    )
    assert validation_error.failed_attempts == failed_attempts

    provider_error = ProviderError(
        "openai", "API error", failed_attempts=failed_attempts
    )
    assert provider_error.failed_attempts == failed_attempts

    config_error = ConfigurationError("Config error", failed_attempts=failed_attempts)
    assert config_error.failed_attempts == failed_attempts


def test_failed_attempts_propagation_through_retry_cycles():
    """Test that failed attempts accumulate and propagate correctly through retry cycles."""
    # Simulate multiple retry attempts with different exceptions
    attempt1 = FailedAttempt(1, ValidationError("Invalid format"), "partial response 1")
    attempt2 = FailedAttempt(2, KeyError("missing_field"), "partial response 2")
    attempt3 = FailedAttempt(3, ValueError("invalid value"), "partial response 3")

    failed_attempts = [attempt1, attempt2, attempt3]

    # Create final retry exception with accumulated failed attempts
    final_exception = InstructorRetryException(
        "All retries exhausted",
        n_attempts=3,
        total_usage=250,
        failed_attempts=failed_attempts,
    )

    # Verify failed attempts are properly stored
    assert final_exception.failed_attempts == failed_attempts
    assert len(final_exception.failed_attempts) == 3

    # Verify attempt numbers are sequential
    attempt_numbers = [
        attempt.attempt_number for attempt in final_exception.failed_attempts
    ]
    assert attempt_numbers == [1, 2, 3]

    # Verify each attempt has different exceptions
    exception_types = [
        type(attempt.exception).__name__ for attempt in final_exception.failed_attempts
    ]
    assert exception_types == ["ValidationError", "KeyError", "ValueError"]

    # Verify completions are preserved
    completions = [attempt.completion for attempt in final_exception.failed_attempts]
    assert completions == [
        "partial response 1",
        "partial response 2",
        "partial response 3",
    ]


def test_failed_attempts_propagation_in_exception_hierarchy():
    """Test that failed attempts propagate correctly through exception inheritance."""
    # Test base class propagation
    base_failed_attempts = [FailedAttempt(1, Exception("Base error"), None)]
    base_error = InstructorError("Base error", failed_attempts=base_failed_attempts)

    # Convert to more specific exception type using from_exception
    specific_error = ValidationError.from_exception(
        base_error, failed_attempts=base_failed_attempts
    )
    assert isinstance(specific_error, ValidationError)
    assert isinstance(specific_error, InstructorError)  # Should still inherit from base
    assert specific_error.failed_attempts == base_failed_attempts

    # Test that derived exceptions maintain failed attempts
    retry_failed_attempts = [
        FailedAttempt(1, Exception("Retry 1"), "completion 1"),
        FailedAttempt(2, Exception("Retry 2"), "completion 2"),
    ]
    retry_error = InstructorRetryException(
        "Retries failed",
        n_attempts=2,
        total_usage=100,
        failed_attempts=retry_failed_attempts,
    )

    # Convert to base type should preserve failed attempts
    base_from_retry = InstructorError.from_exception(
        retry_error, failed_attempts=retry_failed_attempts
    )
    assert base_from_retry.failed_attempts == retry_failed_attempts


def test_failed_attempts_accumulation_simulation():
    """Test simulation of how failed attempts would accumulate in a real retry scenario."""
    # Simulate a retry scenario where attempts accumulate
    attempts = []

    # First attempt fails
    attempts.append(
        FailedAttempt(
            1, ValidationError("Schema validation failed"), {"invalid": "data"}
        )
    )

    # Second attempt fails differently
    attempts.append(
        FailedAttempt(2, JSONDecodeError("Invalid JSON", "", 0), "malformed json")
    )

    # Third attempt fails again
    attempts.append(
        FailedAttempt(
            3, ValidationError("Required field missing"), {"partial": "response"}
        )
    )

    # Final retry exception with all attempts
    final_error = InstructorRetryException(
        "Maximum retries exceeded",
        n_attempts=3,
        total_usage=500,
        failed_attempts=attempts,
        last_completion={"final": "attempt"},
        messages=[{"role": "user", "content": "test"}],
        create_kwargs={"model": "gpt-3.5-turbo", "max_retries": 3},
    )

    # Verify all data is preserved
    assert final_error.n_attempts == 3
    assert final_error.total_usage == 500
    assert len(final_error.failed_attempts) == 3
    assert final_error.last_completion == {"final": "attempt"}

    # Test string representation includes all attempts
    error_str = str(final_error)
    assert "<failed_attempts>" in error_str
    assert "Schema validation failed" in error_str
    assert "Invalid JSON" in error_str
    assert "Required field missing" in error_str
    assert "Maximum retries exceeded" in error_str

    # Verify attempt sequence integrity
    for i, attempt in enumerate(final_error.failed_attempts, 1):
        assert attempt.attempt_number == i


def test_failed_attempts_with_empty_and_none_completions():
    """Test failed attempts handle various completion states correctly."""
    # Test with None completion
    attempt_none = FailedAttempt(1, Exception("Error with None"), None)
    assert attempt_none.completion is None

    # Test with empty string completion
    attempt_empty = FailedAttempt(2, Exception("Error with empty"), "")
    assert attempt_empty.completion == ""

    # Test with empty dict completion
    attempt_empty_dict = FailedAttempt(3, Exception("Error with empty dict"), {})
    assert attempt_empty_dict.completion == {}

    # Test with complex completion
    complex_completion = {
        "choices": [{"message": {"content": "partial"}}],
        "usage": {"total_tokens": 50},
    }
    attempt_complex = FailedAttempt(
        4, Exception("Error with complex"), complex_completion
    )
    assert attempt_complex.completion == complex_completion

    # Create error with mixed completion types
    mixed_attempts = [attempt_none, attempt_empty, attempt_empty_dict, attempt_complex]
    error = InstructorError("Mixed completions", failed_attempts=mixed_attempts)

    # Verify XML rendering handles all types
    error_str = str(error)
    assert "<completion>" in error_str
    assert "</completion>" in error_str
    # Should handle None, empty string, empty dict, and complex objects
    assert error_str.count("<completion>") == 4


def test_failed_attempts_exception_chaining():
    """Test that exception chaining works properly with failed attempts."""
    # Create original exception with failed attempts
    original_attempts = [
        FailedAttempt(1, Exception("Original failure"), "original completion")
    ]
    original_error = InstructorError(
        "Original error", failed_attempts=original_attempts
    )

    try:
        raise original_error
    except InstructorError as e:
        # Create new exception from caught exception, preserving failed attempts
        chained_error = InstructorRetryException(
            "Chained error",
            n_attempts=2,
            total_usage=150,
            failed_attempts=e.failed_attempts,
        )

        # Verify failed attempts are preserved through chaining
        assert chained_error.failed_attempts == original_attempts
        assert len(chained_error.failed_attempts) == 1
        assert chained_error.failed_attempts[0].exception.args[0] == "Original failure"
