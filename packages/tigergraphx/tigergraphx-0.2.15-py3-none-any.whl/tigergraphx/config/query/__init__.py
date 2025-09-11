# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from .node_spec import NodeSpec
from .edge_spec import EdgeSpec
from .neighbor_spec import NeighborSpec

__all__ = [
    "NodeSpec",
    "EdgeSpec",
    "NeighborSpec",
]
