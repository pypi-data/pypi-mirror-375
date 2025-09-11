# Copyright (c) 2025 Marco Pancotti
# This file is part of ThothAI and is released under the Apache License 2.0.
# See the LICENSE.md file in the project root for full license information.

"""ThothAI Qdrant - Native Qdrant implementation for ThothAI Vector Database."""

from .core.base import (
    BaseThothDocument,
    ColumnNameDocument,
    EvidenceDocument,
    SqlDocument,
    ThothType,
    VectorStoreInterface,
)
from .factory import VectorStoreFactory

__version__ = "1.0.0"

__all__ = [
    "BaseThothDocument",
    "ColumnNameDocument",
    "EvidenceDocument",
    "SqlDocument",
    "ThothType",
    "VectorStoreInterface",
    "VectorStoreFactory",
]