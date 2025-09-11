# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Dict
from pathlib import Path
from openai import AsyncOpenAI

from .base_llm_manager import BaseLLMManager
from ..config import OpenAIConfig


class OpenAIManager(BaseLLMManager):
    """
    Manages an asynchronous OpenAI instance for LLM operations.
    """

    config: OpenAIConfig

    def __init__(
        self,
        config: OpenAIConfig | Dict | str | Path,
    ):
        """
        Initialize OpenAIManager with OpenAI settings.

        Args:
            config: Configuration for OpenAI settings.

        Raises:
            ValueError: If the API key is not provided in the configuration.
        """
        config = OpenAIConfig.ensure_config(config)
        super().__init__(config)
        if not self.config.api_key:
            raise ValueError("API key is required to initialize OpenAIManager.")

        # Initialize the LLM immediately
        self._llm: AsyncOpenAI = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            organization=self.config.organization,
            timeout=self.config.request_timeout,
            max_retries=self.config.max_retries,
        )

    def get_llm(self) -> AsyncOpenAI:
        """
        Retrieve the initialized async OpenAI instance.

        Returns:
            The initialized OpenAI instance.
        """
        return self._llm
