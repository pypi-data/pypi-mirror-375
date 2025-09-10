# API Reference

This section provides detailed API reference documentation for the Kura package, automatically generated from the source code using mkdocstrings.

## How to Use This Reference

The API reference is organized by module, with each module containing related classes and functions. For each class, you'll find:

- Constructor parameters and their descriptions
- Instance methods with parameter details and return types
- Properties and attributes

To use these classes in your code, import them from their specific modules:

```python
# Import functions from their specific modules
from kura.summarisation import summarise_conversations, SummaryModel
from kura.cluster import generate_base_clusters_from_conversation_summaries, ClusterDescriptionModel
from kura.meta_cluster import reduce_clusters_from_base_clusters, MetaClusterModel
from kura.dimensionality import reduce_dimensionality_from_clusters, HDBUMAP
from kura.visualization import visualise_pipeline_results
from kura.types import Conversation
from kura.checkpoints import JSONLCheckpointManager
from kura.cache import DiskCacheStrategy
```

## Core Classes

## Procedural API

The procedural API provides a functional approach to conversation analysis with composable pipeline functions.

### Pipeline Functions

::: kura.summarisation.summarise_conversations

::: kura.cluster.generate_base_clusters_from_conversation_summaries

::: kura.meta_cluster.reduce_clusters_from_base_clusters

::: kura.dimensionality.reduce_dimensionality_from_clusters

### Checkpoint Management

::: kura.checkpoint.CheckpointManager

## Implementation Classes

### Embedding Models

::: kura.embedding

### Summarization

::: kura.summarisation

### Clustering

::: kura.cluster

### Meta-Clustering

::: kura.meta_cluster

### Dimensionality Reduction

::: kura.dimensionality
