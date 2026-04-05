import logging

import dspy

from app.core.settings import Settings


logger = logging.getLogger(__name__)


def build_lm(settings: Settings) -> dspy.LM:
    lm_kwargs = {
        "api_base": settings.dspy_api_base,
        "api_key": settings.dspy_api_key,
        "temperature": settings.dspy_temperature,
        "max_tokens": settings.dspy_max_tokens,
        "timeout": settings.dspy_timeout_seconds,
    }

    if settings.dspy_model_type:
        lm_kwargs["model_type"] = settings.dspy_model_type

    return dspy.LM(settings.dspy_model_identifier, **lm_kwargs)


def configure_dspy(settings: Settings) -> dspy.LM:
    lm = build_lm(settings)
    dspy.configure(lm=lm)
    logger.info("Configured DSPy with model '%s'", settings.dspy_model_identifier)
    return lm
