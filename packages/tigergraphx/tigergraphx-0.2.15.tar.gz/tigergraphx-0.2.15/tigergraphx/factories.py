# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Dict, Optional
from pathlib import Path

from tigergraphx.core import Graph
from tigergraphx.config import (
    Settings,
    TigerVectorConfig,
    OpenAIConfig,
    OpenAIEmbeddingConfig,
    OpenAIChatConfig,
)
from tigergraphx.llm import (
    OpenAIManager,
    OpenAIChat,
)
from tigergraphx.vector_search import (
    OpenAIEmbedding,
    TigerVectorManager,
    TigerVectorSearchEngine,
)


def create_openai_components(
    config: Settings | Path | str | Dict, graph: Optional[Graph] = None
) -> tuple[OpenAIChat, TigerVectorSearchEngine]:
    """
    Creates an OpenAIChat instance and a TigerVectorSearchEngine
    from a shared configuration. Reuses the same OpenAIManager instance for both components.
    """
    # Ensure configuration is a Settings instance
    settings = Settings.ensure_config(config)

    # Validate configuration types
    if not isinstance(settings.vector_db, TigerVectorConfig):
        raise TypeError(
            "Expected `vector_db` to be an instance of TigerVectorConfig."
        )
    if not isinstance(settings.llm, OpenAIConfig):
        raise TypeError("Expected `llm` to be an instance of OpenAIConfig.")
    if not isinstance(settings.embedding, OpenAIEmbeddingConfig):
        raise TypeError(
            "Expected `embedding` to be an instance of OpenAIEmbeddingConfig."
        )
    if not isinstance(settings.chat, OpenAIChatConfig):
        raise TypeError("Expected `chat` to be an instance of OpenAIChatConfig.")

    # Initialize shared OpenAIManager
    llm_manager = OpenAIManager(settings.llm)

    # Initialize OpenAIChat
    openai_chat = OpenAIChat(
        llm_manager=llm_manager,
        config=settings.chat,
    )

    embedding = OpenAIEmbedding(llm_manager, settings.embedding)

    if graph is None:
        raise ValueError("Graph cannot be None when TigerVector is used.")
    tigervector_manager = TigerVectorManager(settings.vector_db, graph)
    search_engine = TigerVectorSearchEngine(embedding, tigervector_manager)

    # Return both instances
    return openai_chat, search_engine
