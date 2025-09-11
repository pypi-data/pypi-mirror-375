# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Optional
from pydantic import Field

from ..base_config import BaseConfig


class BaseLLMConfig(BaseConfig):
    """Base configuration class for LLM."""

    type: str = Field(description="Mandatory type field for identifying the LLM type.")


class OpenAIConfig(BaseLLMConfig):
    """Configuration class for OpenAI."""

    type: str = Field(default="OpenAI", description="Default type for OpenAIConfig.")
    api_key: str = Field(
        alias="OPENAI_API_KEY", description="API key for authentication with OpenAI."
    )
    base_url: Optional[str] = Field(
        default=None, description="Custom base URL for OpenAI API."
    )
    organization: Optional[str] = Field(
        default=None, description="OpenAI organization ID (if applicable)."
    )
    max_retries: int = Field(
        default=10, description="Maximum number of retries for failed API requests."
    )
    request_timeout: float = Field(
        default=180.0, description="Request timeout in seconds."
    )
