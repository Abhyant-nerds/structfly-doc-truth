from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any


ValidationResult = tuple[bool, str | None]


def append_processing_error(state: dict[str, Any], stage: str, message: str) -> None:
    errors = state.setdefault("processing_errors", [])
    errors.append({"stage": stage, "message": message})


def invoke_with_retries(
    *,
    state: dict[str, Any],
    stage: str,
    invoke: Callable[[], Any],
    validate: Callable[[Any], ValidationResult] | None,
    logger: logging.Logger,
    max_attempts: int,
) -> Any | None:
    last_error_message: str | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            result = invoke()
            if validate is not None:
                is_valid, validation_error = validate(result)
                if not is_valid:
                    raise ValueError(validation_error or "DSPy output failed validation")

            return result
        except Exception as exc:
            last_error_message = str(exc)
            logger.warning(
                "DSPy stage '%s' failed on attempt %s/%s: %s",
                stage,
                attempt,
                max_attempts,
                exc,
            )

    final_message = (
        f"DSPy stage '{stage}' failed after {max_attempts} attempts: "
        f"{last_error_message or 'unknown error'}"
    )
    logger.error(final_message)
    append_processing_error(state, stage, final_message)
    return None
