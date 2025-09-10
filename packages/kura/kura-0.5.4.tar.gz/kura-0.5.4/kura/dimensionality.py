from kura.base_classes import BaseDimensionalityReduction, BaseEmbeddingModel
from kura.base_classes.checkpoint import BaseCheckpointManager
from kura.types import Cluster, ProjectedCluster
from kura.embedding import OpenAIEmbeddingModel
from kura.utils import calculate_cluster_levels
from typing import Union, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class HDBUMAP(BaseDimensionalityReduction):
    @property
    def checkpoint_filename(self) -> str:
        """The filename to use for checkpointing this model's output."""
        return "dimensionality"

    def __init__(
        self,
        embedding_model: BaseEmbeddingModel = OpenAIEmbeddingModel(),
        n_components: int = 2,
        min_dist: float = 0.1,
        metric: str = "cosine",
        n_neighbors: Union[int, None] = None,
    ):
        self.embedding_model = embedding_model
        self.n_components = n_components
        self.min_dist = min_dist
        self.metric = metric
        self.n_neighbors = n_neighbors
        logger.info(
            f"Initialized HDBUMAP with embedding_model={type(embedding_model).__name__}, n_components={n_components}, min_dist={min_dist}, metric={metric}, n_neighbors={n_neighbors}"
        )

    async def reduce_dimensionality(
        self, clusters: list[Cluster]
    ) -> list[ProjectedCluster]:
        # Embed all clusters
        from umap import UMAP

        if not clusters:
            logger.warning("Empty clusters list provided to reduce_dimensionality")
            return []

        logger.info(f"Starting dimensionality reduction for {len(clusters)} clusters")
        texts_to_embed = [str(c) for c in clusters]

        try:
            cluster_embeddings = await self.embedding_model.embed(texts_to_embed)
            logger.debug(f"Generated embeddings for {len(clusters)} clusters")
        except Exception as e:
            logger.error(f"Failed to generate embeddings for clusters: {e}")
            raise

        if not cluster_embeddings or len(cluster_embeddings) != len(texts_to_embed):
            logger.error(
                f"Error: Number of embeddings ({len(cluster_embeddings) if cluster_embeddings else 0}) does not match number of clusters ({len(texts_to_embed)}) or embeddings are empty."
            )
            return []

        embeddings = np.array(cluster_embeddings)
        logger.debug(f"Created embedding matrix of shape {embeddings.shape}")

        # Project to 2D using UMAP
        n_neighbors_actual = (
            self.n_neighbors if self.n_neighbors else min(15, len(embeddings) - 1)
        )
        logger.debug(
            f"Using UMAP with n_neighbors={n_neighbors_actual}, min_dist={self.min_dist}, metric={self.metric}"
        )

        try:
            umap_reducer = UMAP(
                n_components=self.n_components,
                n_neighbors=n_neighbors_actual,
                min_dist=self.min_dist,
                metric=self.metric,
            )
            reduced_embeddings = umap_reducer.fit_transform(embeddings)
            logger.info(
                f"UMAP dimensionality reduction completed: {embeddings.shape} -> {reduced_embeddings.shape}"  # type: ignore
            )
        except Exception as e:
            logger.error(f"UMAP dimensionality reduction failed: {e}")
            raise

        # Create projected clusters with 2D coordinates
        res = []
        for i, cluster in enumerate(clusters):
            projected = ProjectedCluster(
                slug=cluster.slug,
                id=cluster.id,
                name=cluster.name,
                description=cluster.description,
                chat_ids=cluster.chat_ids,
                parent_id=cluster.parent_id,
                x_coord=float(reduced_embeddings[i][0]),  # pyright: ignore
                y_coord=float(reduced_embeddings[i][1]),  # pyright: ignore
                level=0,
            )
            res.append(projected)

        res = calculate_cluster_levels(res)

        logger.info(f"Successfully created {len(res)} projected clusters")
        return res


async def reduce_dimensionality_from_clusters(
    clusters: list[Cluster],
    *,
    model: BaseDimensionalityReduction,
    checkpoint_manager: Optional[BaseCheckpointManager] = None,
) -> list[ProjectedCluster]:
    """Reduce dimensions of clusters for visualization.

    Projects clusters to 2D space using the provided dimensionality reduction model.
    Supports different algorithms (UMAP, t-SNE, PCA, etc.) through the model interface.

    Args:
        clusters: List of clusters to project
        model: Dimensionality reduction model to use (UMAP, t-SNE, etc.)
        checkpoint_manager: Optional checkpoint manager for caching

    Returns:
        List of projected clusters with 2D coordinates

    Example:
        >>> dim_model = HDBUMAP(n_components=2)
        >>> projected = await reduce_dimensionality(
        ...     clusters=hierarchical_clusters,
        ...     model=dim_model,
        ...     checkpoint_manager=checkpoint_mgr
        ... )
    """
    logger.info(
        f"Starting dimensionality reduction for {len(clusters)} clusters using {type(model).__name__}"
    )

    # Try to load from checkpoint
    if checkpoint_manager:
        cached = checkpoint_manager.load_checkpoint(
            model.checkpoint_filename, ProjectedCluster
        )
        if cached:
            logger.info(f"Loaded {len(cached)} projected clusters from checkpoint")
            return cached

    # Reduce dimensionality
    logger.info("Projecting clusters to 2D space...")
    projected_clusters = await model.reduce_dimensionality(clusters)
    logger.info(f"Projected {len(projected_clusters)} clusters to 2D")

    # Save to checkpoint
    if checkpoint_manager:
        checkpoint_manager.save_checkpoint(
            model.checkpoint_filename, projected_clusters
        )

    return projected_clusters
